import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sdr_copilot.settings')
application = get_wsgi_application()

try:
    from init_admin import ensure_admin_exists
    ensure_admin_exists()
except Exception as e:
    print(f"[WSGI ADMIN INIT NOTICE] {e}")

