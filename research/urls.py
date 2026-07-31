from django.urls import path
from . import views

app_name = 'research'

urlpatterns = [
    path('', views.research_form_view, name='index'),
    path('', views.research_form_view, name='form'),
    path('history/', views.company_history_view, name='history'),
    path('detail/<int:pk>/', views.research_detail_view, name='detail'),
    path('export/pdf/<int:pk>/', views.export_company_pdf, name='export_pdf'),
    path('export/txt/<int:pk>/', views.export_company_txt, name='export_txt'),
    
    # REST API Endpoints
    path('api/', views.api_company_list, name='api_list'),
    path('api/<int:pk>/', views.api_company_detail, name='api_detail'),
]
