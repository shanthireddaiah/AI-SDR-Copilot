from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.copilot_chat_view, name='index'),
    path('history/', views.chat_history_list_view, name='history'),
    path('export/pdf/<int:pk>/', views.export_chat_pdf, name='export_pdf'),
    path('export/txt/<int:pk>/', views.export_chat_txt, name='export_txt'),
    
    # REST API Endpoints
    path('api/', views.api_chat_post, name='api_chat_post'),
    path('api/history/', views.api_chat_history, name='api_chat_history'),
]
