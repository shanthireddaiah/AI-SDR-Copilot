from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from research.models import Company
from research.services import generate_company_research, generate_outreach_messages, is_demo_mode

class Phase2ResearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'sdr_tester'
        self.password = 'Pass12345!'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

    def test_demo_mode_detector(self):
        self.assertTrue(is_demo_mode())

    def test_company_research_service(self):
        result = generate_company_research("Acme Corp", "https://acme.com", "Manufacturing", "Makes widgets")
        self.assertIn("overview", result)
        self.assertIn("products", result)
        self.assertIn("pain_points", result)
        self.assertIn("sales_insights", result)
        self.assertIn("Acme Corp", result["overview"])

    def test_outreach_service(self):
        messages = generate_outreach_messages("Acme Corp", "Manufacturing", "Overview text", "Products text", "Pain points text")
        self.assertIn("email_outreach", messages)
        self.assertIn("linkedin_outreach", messages)
        self.assertIn("cold_call_script", messages)
        self.assertIn("Acme Corp", messages["email_outreach"])

    def test_post_company_research_view(self):
        response = self.client.post(reverse('research:form'), {
            'name': 'Stripe',
            'website': 'https://stripe.com',
            'industry': 'FinTech',
            'user_description': 'Online payment infrastructure'
        })
        
        self.assertTrue(Company.objects.filter(name='Stripe', user=self.user).exists())
        company = Company.objects.get(name='Stripe', user=self.user)
        self.assertRedirects(response, reverse('research:detail', kwargs={'pk': company.id}))
        
        self.assertIsNotNone(company.overview)
        self.assertIsNotNone(company.products)

    def test_company_detail_view(self):
        company = Company.objects.create(
            user=self.user,
            name="Nike",
            overview="Nike overview",
            email_outreach="Nike cold email"
        )
        response = self.client.get(reverse('research:detail', kwargs={'pk': company.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nike")

    def test_api_company_list_post(self):
        response = self.client.post(
            reverse('research:api_list'),
            data={'name': 'Stripe', 'website': 'https://stripe.com', 'industry': 'FinTech'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json().get('name'), 'Stripe')
