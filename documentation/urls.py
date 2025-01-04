from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api

app_name = 'documentation'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'documents', api.DocumentViewSet, basename='document')
router.register(r'categories', api.CategoryViewSet, basename='category')
router.register(r'attachments', api.AttachmentViewSet, basename='attachment')

urlpatterns = [
    # Document URLs
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('create/', views.DocumentCreateView.as_view(), name='document_create'),
    path('document/<slug:slug>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('document/<slug:slug>/update/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('document/<slug:slug>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Tag URLs
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    
    # Attachment URLs
    path('attachments/<int:pk>/delete/', views.delete_attachment, name='delete_attachment'),

    # API URLs
    path('api/', include(router.urls)),
]
