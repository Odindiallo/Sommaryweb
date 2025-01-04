from django.urls import path
from . import views

app_name = 'url_summarizer'

urlpatterns = [
    path('', views.summarizer_view, name='summarizer'),
    path('summarize/', views.summarize_url, name='summarize_url'),
    path('create-document/', views.create_document, name='create_document'),
    path('analyze-website/', views.analyze_website, name='analyze_website'),
    path('website-analyzer/', views.website_analyzer_view, name='website_analyzer'),
]
