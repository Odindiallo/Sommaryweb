from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db.models import Count, Q
from django.contrib.postgres.search import SearchQuery, SearchRank
from .models import Document, Category, Attachment
from .forms import DocumentForm
from taggit.models import Tag
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

class DocumentListView(ListView):
    model = Document
    template_name = 'documentation/document_list.html'
    context_object_name = 'documents'
    paginate_by = 12
    
    def get_queryset(self):
        # Get search parameters from request
        query = self.request.GET.get('q')
        category_slug = self.request.GET.get('category')
        tags = self.request.GET.getlist('tag')
        sort_by = self.request.GET.get('sort', 'recent')
        author_id = self.request.GET.get('author')

        # Get category if specified
        category = None
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)

        # Get author if specified
        author = None
        if author_id:
            author = get_object_or_404(get_user_model(), id=author_id)

        # Apply search
        queryset = Document.search(
            query=query,
            category=category,
            tags=tags,
            sort_by=sort_by,
            author=author
        )

        # Filter by public status for non-staff users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True)
        elif not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(is_public=True) | Q(author=self.request.user)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(doc_count=Count('documents'))
        context['tags'] = Tag.objects.annotate(doc_count=Count('taggit_taggeditem_items'))
        context['sort_options'] = [
            ('recent', 'Most Recent'),
            ('views', 'Most Viewed'),
            ('title', 'Title A-Z'),
            ('relevance', 'Relevance')
        ]
        context['current_sort'] = self.request.GET.get('sort', 'recent')
        context['current_category'] = self.request.GET.get('category')
        context['current_tags'] = self.request.GET.getlist('tag')
        context['current_query'] = self.request.GET.get('q', '')
        return context

class DocumentDetailView(DetailView):
    model = Document
    template_name = 'documentation/document_detail.html'
    context_object_name = 'document'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.increment_views()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related documents based on category and tags
        related_docs = Document.objects.filter(
            Q(category=self.object.category) |
            Q(tags__in=self.object.tags.all())
        ).exclude(id=self.object.id).distinct()
        
        # Filter by public status for non-staff users
        if not self.request.user.is_authenticated:
            related_docs = related_docs.filter(is_public=True)
        elif not self.request.user.is_staff:
            related_docs = related_docs.filter(
                Q(is_public=True) | Q(author=self.request.user)
            )
        
        context['related_documents'] = related_docs[:3]
        return context

@method_decorator(csrf_protect, name='dispatch')
class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documentation/document_form.html'
    success_url = reverse_lazy('documentation:document_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        return response

@method_decorator(csrf_protect, name='dispatch')
class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documentation/document_form.html'
    success_url = reverse_lazy('documentation:document_list')

    def get_queryset(self):
        # Only allow users to edit their own documents
        return Document.objects.filter(author=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

@method_decorator(csrf_protect, name='dispatch')
class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'documentation/document_confirm_delete.html'
    success_url = reverse_lazy('documentation:document_list')

    def get_queryset(self):
        # Only allow users to delete their own documents
        return Document.objects.filter(author=self.request.user)

class CategoryListView(ListView):
    model = Category
    template_name = 'documentation/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.annotate(document_count=Count('documents'))

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'documentation/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.documents.filter(is_public=True)
        return context

class TagListView(ListView):
    model = Tag
    template_name = 'documentation/tag_list.html'
    context_object_name = 'tags'

    def get_queryset(self):
        return Tag.objects.annotate(document_count=Count('taggit_taggeditem_items'))

class TagDetailView(DetailView):
    model = Tag
    template_name = 'documentation/tag_detail.html'
    context_object_name = 'tag'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = Document.objects.filter(tags=self.object, is_public=True)
        return context

@login_required
def delete_attachment(request, pk):
    if request.method == 'POST':
        attachment = get_object_or_404(Attachment, pk=pk)
        if attachment.document.author == request.user:
            attachment.delete()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=403)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
