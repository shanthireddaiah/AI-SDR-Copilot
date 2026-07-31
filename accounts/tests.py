from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from research.models import Company
from rag.models import UploadedDocument
from chat.models import ChatHistory

class Phase1VerificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.email = 'testuser@example.com'
        self.password = 'TestPassword123'
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    def test_registration_view(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

        reg_response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'NewPass1234!',
            'password2': 'NewPass1234!'
        })
        self.assertRedirects(reg_response, reverse('dashboard:index'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_logout_view(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

        login_response = self.client.post(reverse('accounts:login'), {
            'username': self.username,
            'password': self.password
        })
        self.assertRedirects(login_response, reverse('dashboard:index'))

        logout_response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(logout_response, reverse('accounts:login'))

    def test_password_reset_views(self):
        response = self.client.get(reverse('accounts:password_reset'))
        self.assertEqual(response.status_code, 200)

        response_done = self.client.get(reverse('accounts:password_reset_done'))
        self.assertEqual(response_done.status_code, 200)

    def test_dashboard_authenticated_access(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next=/")

        self.client.login(username=self.username, password=self.password)
        auth_response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(auth_response.status_code, 200)

    def test_all_sidebar_views(self):
        self.client.login(username=self.username, password=self.password)
        
        res_response = self.client.get(reverse('research:form'))
        self.assertEqual(res_response.status_code, 200)

        rag_response = self.client.get(reverse('rag:index'))
        self.assertEqual(rag_response.status_code, 200)

        chat_response = self.client.get(reverse('chat:index'))
        self.assertEqual(chat_response.status_code, 200)

    def test_models_creation(self):
        company = Company.objects.create(
            user=self.user,
            name="Test Corp",
            website="https://testcorp.com",
            industry="Technology",
            user_description="SaaS test company"
        )
        self.assertEqual(str(company), "Test Corp")

        chat = ChatHistory.objects.create(
            user=self.user,
            company=company,
            question="How to approach?",
            answer="Position value proposition."
        )
        self.assertIn("Test Corp", str(chat.company))
