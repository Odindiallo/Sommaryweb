from django.urls import path
from . import views

app_name = 'url_summarizer'

urlpatterns = [
    path('', views.summarizer_view, name='summarizer'),
    path('summarize/', views.summarize_url, name='summarize_url'),
    path('create-document/', views.create_document, name='create_document'),
]
