from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='profile_user', password='password123')
        self.client = Client()
        self.client.login(username='profile_user', password='password123')

    def test_user_profile_creation_signal(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.role, UserProfile.ROLE_USER)

    def test_settings_view(self):
        response = self.client.get('/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "profile_user")
