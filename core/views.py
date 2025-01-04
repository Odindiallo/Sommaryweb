from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count
from documentation.models import Document, Category
from django.contrib.auth import get_user_model
from taggit.models import Tag

# Create your views here.

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recent documents
        context['recent_documents'] = Document.objects.filter(is_public=True).order_by('-created_at')[:6]
        
        # Get all categories
        context['categories'] = Category.objects.annotate(doc_count=Count('documents')).order_by('name')
        
        # Get statistics
        context['total_documents'] = Document.objects.count()
        context['total_categories'] = Category.objects.count()
        context['total_authors'] = get_user_model().objects.filter(documents__isnull=False).distinct().count()
        context['total_tags'] = Tag.objects.count()
        
        return context
