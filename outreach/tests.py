from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import OutreachMessage
from research.models import Company

class OutreachTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='outreach_user', password='password123')
        self.client = Client()
        self.client.login(username='outreach_user', password='password123')
        self.company = Company.objects.create(
            user=self.user,
            name="Test Corp",
            industry="Software"
        )

    def test_create_outreach_message(self):
        msg = OutreachMessage.objects.create(
            user=self.user,
            company=self.company,
            message_type=OutreachMessage.TYPE_COLD_EMAIL,
            subject="Test Cold Email",
            content="Hello test prospect."
        )
        self.assertEqual(OutreachMessage.objects.count(), 1)
        self.assertEqual(msg.company.name, "Test Corp")

    def test_outreach_list_view(self):
        OutreachMessage.objects.create(
            user=self.user,
            company=self.company,
            message_type=OutreachMessage.TYPE_COLD_EMAIL,
            subject="Test Email",
            content="Content body"
        )
        response = self.client.get('/outreach/history/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Email")

    def test_export_txt_view(self):
        msg = OutreachMessage.objects.create(
            user=self.user,
            company=self.company,
            message_type=OutreachMessage.TYPE_COLD_EMAIL,
            subject="Export Test",
            content="Exportable plain text."
        )
        response = self.client.get(f'/outreach/export/txt/{msg.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
