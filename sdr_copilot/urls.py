from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

# Custom Error Views for 404 & 500
def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)

def custom_500_view(request):
    return render(request, '500.html', status=500)

handler404 = 'sdr_copilot.urls.custom_404_view'
handler500 = 'sdr_copilot.urls.custom_500_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('research/', include('research.urls')),
    path('outreach/', include('outreach.urls')),
    path('rag/', include('rag.urls')),
    path('chat/', include('chat.urls')),
    path('settings/', include('settings.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
