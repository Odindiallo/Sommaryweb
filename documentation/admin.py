from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
import csv
from .models import Category, Document, Attachment

class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        # Get statistics
        extra_context = extra_context or {}
        extra_context['total_documents'] = Document.objects.count()
        extra_context['total_categories'] = Category.objects.count()
        extra_context['total_users'] = User.objects.count()
        return super().index(request, extra_context)

# Create custom admin site instance
admin_site = CustomAdminSite(name='docadmin')

admin_site.site_header = "Documentation Management"
admin_site.site_title = "Documentation Admin"
admin_site.index_title = "Documentation Administration"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'document_count']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def document_count(self, obj):
        return obj.documents.count()
    document_count.short_description = 'Documents'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(doc_count=Count('documents'))

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1
    readonly_fields = ['file_size', 'content_type', 'human_readable_size', 'preview']
    
    def preview(self, obj):
        if obj.content_type and obj.content_type.startswith('image/'):
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.file.url)
        return "No preview available"
    preview.short_description = 'Preview'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'author_link', 'category', 'is_public', 'views', 'created_at', 'tag_list']
    list_filter = ['is_public', 'category', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [AttachmentInline]
    readonly_fields = ['views', 'created_at', 'updated_at']
    actions = ['make_public', 'make_private', 'export_as_csv']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('Settings', {
            'fields': ('is_public', 'views'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)\
            .select_related('author', 'category')
    
    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'
    
    def author_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.username)
    author_link.short_description = 'Author'
    
    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} documents were marked as public.')
    make_public.short_description = "Mark selected documents as public"
    
    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} documents were marked as private.')
    make_private.short_description = "Mark selected documents as private"
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = ['title', 'author', 'category', 'content', 'created_at', 'updated_at']
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.model_name}_export.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            row = [getattr(obj, field) for field in field_names]
            writer.writerow(row)
        
        return response
    export_as_csv.short_description = "Export selected documents as CSV"
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['author'].initial = request.user
            form.base_fields['author'].disabled = True
        return form
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new document
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'document_link', 'file_size', 'content_type', 'uploaded_at', 'preview_thumbnail']
    list_filter = ['content_type', 'uploaded_at']
    search_fields = ['name', 'document__title']
    readonly_fields = ['file_size', 'content_type', 'human_readable_size', 'preview_large']
    
    def document_link(self, obj):
        url = reverse('admin:documentation_document_change', args=[obj.document.id])
        return format_html('<a href="{}">{}</a>', url, obj.document.title)
    document_link.short_description = 'Document'
    
    def preview_thumbnail(self, obj):
        if obj.content_type and obj.content_type.startswith('image/'):
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.file.url)
        return "No preview available"
    preview_thumbnail.short_description = 'Preview'
    
    def preview_large(self, obj):
        if obj.content_type and obj.content_type.startswith('image/'):
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.file.url)
        return "No preview available"
    preview_large.short_description = 'Large Preview'

# Register models with custom admin site
admin_site.register(Category, CategoryAdmin)
admin_site.register(Document, DocumentAdmin)
admin_site.register(Attachment, AttachmentAdmin)
admin_site.register(User, UserAdmin)
