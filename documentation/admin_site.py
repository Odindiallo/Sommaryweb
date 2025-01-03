from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Document, Category, Attachment

class DocumentationAdminSite(AdminSite):
    site_header = 'Documentation Management'
    site_title = 'Documentation Admin'
    index_title = 'Documentation Administration'
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        return app_list
    
    def index(self, request, extra_context=None):
        """
        Override the default index to add custom dashboard widgets
        """
        # Recent Documents
        recent_documents = Document.objects.select_related('author', 'category')\
            .order_by('-created_at')[:5]
            
        # Most Active Users (authors with most documents)
        active_users = Document.objects.values('author__username')\
            .annotate(doc_count=Count('id'))\
            .order_by('-doc_count')[:5]
            
        # Popular Categories
        popular_categories = Category.objects.annotate(
            doc_count=Count('documents')
        ).order_by('-doc_count')[:5]
        
        # Document Statistics
        total_documents = Document.objects.count()
        public_documents = Document.objects.filter(is_public=True).count()
        total_views = Document.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
        
        # Recent Activity
        last_week = timezone.now() - timedelta(days=7)
        recent_activity = {
            'new_documents': Document.objects.filter(created_at__gte=last_week).count(),
            'new_attachments': Attachment.objects.filter(uploaded_at__gte=last_week).count(),
        }
        
        context = {
            'recent_documents': recent_documents,
            'active_users': active_users,
            'popular_categories': popular_categories,
            'total_documents': total_documents,
            'public_documents': public_documents,
            'total_views': total_views,
            'recent_activity': recent_activity,
            **(extra_context or {})
        }
        
        return super().index(request, context)
