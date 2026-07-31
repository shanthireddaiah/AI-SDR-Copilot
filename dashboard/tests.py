from django.test import TestCase, Client
from django.contrib.auth.models import User
from research.models import Company

class DashboardTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dash_user', password='password123')
        self.client = Client()
        self.client.login(username='dash_user', password='password123')
        Company.objects.create(user=self.user, name="Acme Corp", industry="Tech")

    def test_dashboard_index_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Acme Corp")
