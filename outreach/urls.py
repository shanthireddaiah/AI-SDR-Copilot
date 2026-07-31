from django.urls import path
from . import views

app_name = 'outreach'

urlpatterns = [
    path('generate/', views.generate_outreach_view, name='generate'),
    path('history/', views.outreach_list_view, name='history'),
    path('detail/<int:pk>/', views.outreach_detail_view, name='detail'),
    path('export/pdf/<int:pk>/', views.export_outreach_pdf, name='export_pdf'),
    path('export/txt/<int:pk>/', views.export_outreach_txt, name='export_txt'),
    path('api/generate/', views.api_generate_outreach, name='api_generate'),
]
