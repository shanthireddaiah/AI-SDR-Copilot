from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    Stores extended profile preferences and role assignment for users.
    Supports Role-Based Access Control (RBAC): Admin vs Standard User.
    """
    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrator'),
        (ROLE_USER, 'Standard SDR User'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER, help_text="User System Role")
    job_title = models.CharField(max_length=255, blank=True, default="Sales Development Representative")
    target_industry = models.CharField(max_length=255, blank=True, default="Software & SaaS")
    preferred_tone = models.CharField(max_length=50, default="Professional & Consultative")
    custom_openai_key = models.CharField(max_length=255, blank=True, help_text="User specific OpenAI API Key (optional override)")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile ({self.get_role_display()})"

    @property
    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN or self.user.is_superuser or self.user.is_staff


# Signal to auto-create UserProfile whenever a User is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = UserProfile.ROLE_ADMIN if instance.is_superuser else UserProfile.ROLE_USER
        UserProfile.objects.create(user=instance, role=role)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
