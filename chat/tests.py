from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import ChatHistory
from .graph import run_sales_copilot_workflow

class ChatTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='chat_user', password='password123')
        self.client = Client()
        self.client.login(username='chat_user', password='password123')

    def test_langgraph_workflow_demo_mode(self):
        response_text = run_sales_copilot_workflow(
            question="What is the best pitch for our enterprise software?",
            user_id=self.user.id
        )
        self.assertIn("AI Sales Recommendation", response_text)

    def test_chat_history_creation(self):
        chat = ChatHistory.objects.create(
            user=self.user,
            question="How do I contact decision makers?",
            answer="Send personalized cold emails highlighting ROI."
        )
        self.assertEqual(ChatHistory.objects.count(), 1)
        self.assertEqual(chat.user.username, 'chat_user')

    def test_copilot_chat_view(self):
        response = self.client.get('/chat/')
        self.assertEqual(response.status_code, 200)
