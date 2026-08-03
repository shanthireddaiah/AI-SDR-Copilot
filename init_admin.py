import os
import django

def ensure_admin_exists():
    try:
        from django.contrib.auth.models import User
        from settings.models import UserProfile

        username = os.environ.get('ADMIN_USERNAME', 'shanthi')
        email = os.environ.get('ADMIN_EMAIL', 'shanthi3059@gmail.com')
        password = os.environ.get('ADMIN_PASSWORD', 'Reddaiah@3059')

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_superuser(username=username, email=email, password=password)
            print(f"[AUTO-ADMIN] Created superuser '{username}'.")
        else:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            print(f"[AUTO-ADMIN] Updated superuser '{username}'.")

        # Ensure profile has ROLE_ADMIN
        if hasattr(user, 'profile'):
            user.profile.role = UserProfile.ROLE_ADMIN
            user.profile.save()
        else:
            UserProfile.objects.create(user=user, role=UserProfile.ROLE_ADMIN)

        print(f"[AUTO-ADMIN] Admin user '{username}' is ready.")
    except Exception as e:
        print(f"[AUTO-ADMIN NOTICE] {e}")

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sdr_copilot.settings')
    django.setup()
    ensure_admin_exists()
