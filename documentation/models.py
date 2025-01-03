from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.contrib.postgres.search import SearchVectorField, SearchVector, SearchQuery, SearchRank
from django.db.models import F, Value, Q
from django.contrib.postgres.indexes import GinIndex
from taggit.managers import TaggableManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.functions import Coalesce
from django.db import connection
from ckeditor.fields import RichTextField
import uuid
import os
import mimetypes

User = get_user_model()

def attachment_upload_path(instance, filename):
    """Generate upload path for attachments"""
    return f'attachments/{instance.document.slug}/{filename}'

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Document(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = RichTextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='documents')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    tags = TaggableManager()
    is_public = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True)
    # New fields for hierarchical structure
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.PositiveIntegerField(default=0)
    is_index = models.BooleanField(default=False, help_text="Whether this document is the main page of its section")

    class Meta:
        ordering = ['order', 'title']
        indexes = [
            GinIndex(fields=['search_vector']),
            models.Index(fields=['title']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_public']),
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('documentation:document_detail', kwargs={'slug': self.slug})

    def increment_views(self):
        Document.objects.filter(pk=self.pk).update(views=F('views') + 1)

    def get_hierarchy(self):
        """Get the full hierarchy of the document including siblings and children."""
        if self.parent:
            return {
                'parent': self.parent,
                'siblings': self.parent.children.all(),
                'children': self.children.all(),
            }
        return {
            'parent': None,
            'siblings': Document.objects.filter(parent=None),
            'children': self.children.all(),
        }

    @staticmethod
    def search(query=None, category=None, tags=None, sort_by='recent', author=None):
        queryset = Document.objects.all()

        if query and connection.vendor == 'postgresql':
            search_query = SearchQuery(query)
            queryset = queryset.filter(search_vector=search_query)
            queryset = queryset.annotate(rank=SearchRank('search_vector', search_query))
        elif query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query)
            )

        if category:
            queryset = queryset.filter(category=category)

        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__name__in=[tag])

        if author:
            queryset = queryset.filter(author=author)

        # Apply sorting
        if sort_by == 'relevance' and query and connection.vendor == 'postgresql':
            queryset = queryset.order_by('-rank', '-created_at')
        elif sort_by == 'views':
            queryset = queryset.order_by('-views', '-created_at')
        elif sort_by == 'title':
            queryset = queryset.order_by('title', '-created_at')
        else:  # recent
            queryset = queryset.order_by('-created_at')

        return queryset.distinct()

@receiver(post_save, sender=Document)
def update_search_vector(sender, instance, **kwargs):
    """Update search_vector after the document is saved."""
    if instance.pk and connection.vendor == 'postgresql':  # Only update if using PostgreSQL
        # Get the tag names as a list
        tag_names = list(instance.tags.values_list('name', flat=True))
        tag_vector = SearchVector(Value(' '.join(tag_names)), weight='C')
        
        # Create and combine the search vectors
        Document.objects.filter(pk=instance.pk).update(
            search_vector=(
                SearchVector('title', weight='A') +
                SearchVector('content', weight='B') +
                tag_vector
            )
        )

class Attachment(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=attachment_upload_path)
    name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveIntegerField(null=True, editable=False)
    content_type = models.CharField(max_length=100, null=True, editable=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.name or os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        if self.file:
            if not self.name:
                self.name = os.path.basename(self.file.name)
            try:
                self.file_size = self.file.size
            except:
                self.file_size = 0
            # Use mimetypes to guess content type if not provided
            if not self.content_type:
                self.content_type = mimetypes.guess_type(self.file.name)[0] or 'application/octet-stream'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the file from storage when the attachment is deleted
        storage = self.file.storage
        if storage.exists(self.file.name):
            storage.delete(self.file.name)
        super().delete(*args, **kwargs)

    @property
    def file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()

    @property
    def is_image(self):
        """Check if the file is an image."""
        image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        return self.content_type in image_types

    @property
    def is_pdf(self):
        """Check if the file is a PDF."""
        return self.content_type == 'application/pdf'

    @property
    def human_readable_size(self):
        """Convert file size to human readable format"""
        if self.file_size is None:
            return "0 B"
            
        size = float(self.file_size)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
