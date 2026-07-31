from django.db import models
from django.contrib.auth.models import User
from research.models import Company

class ChatHistory(models.Model):
    """
    Stores Q&A conversation sessions between the user and the AI Sales Copilot.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='chats')
    question = models.TextField(help_text="User prompt or question")
    answer = models.TextField(help_text="AI Sales Copilot generated response")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Chat Histories"

    def __str__(self):
        return f"Chat with {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
