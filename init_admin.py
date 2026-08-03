import os
import django

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sdr_copilot.settings')
django.setup()

from django.contrib.auth.models import User
from settings.models import UserProfile

def create_or_update_admin():
    username = os.environ.get('ADMIN_USERNAME', 'shanthi')
    email = os.environ.get('ADMIN_EMAIL', 'shanthi3059@gmail.com')
    password = os.environ.get('ADMIN_PASSWORD', 'Reddaiah@3059')

    print(f"Checking admin user '{username}'...")

    if not User.objects.filter(username=username).exists():
        user = User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Created superuser '{username}'.")
    else:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        print(f"Updated password for superuser '{username}'.")

    # Ensure profile has ROLE_ADMIN
    if hasattr(user, 'profile'):
        user.profile.role = UserProfile.ROLE_ADMIN
        user.profile.save()
    else:
        UserProfile.objects.create(user=user, role=UserProfile.ROLE_ADMIN)
    
    print(f"Admin user '{username}' is configured and ready.")

if __name__ == '__main__':
    create_or_update_admin()
