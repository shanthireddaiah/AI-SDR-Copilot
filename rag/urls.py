from django.urls import path
from . import views

app_name = 'rag'

urlpatterns = [
    path('', views.knowledge_base_view, name='index'),
    path('query/', views.rag_query_ajax, name='query_ajax'),
    
    # REST API Endpoints
    path('api/upload/', views.api_upload_pdf, name='api_upload'),
    path('api/query/', views.api_rag_query, name='api_query'),
]
