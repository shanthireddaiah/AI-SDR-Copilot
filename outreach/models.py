from django.db import models
from django.contrib.auth.models import User
from research.models import Company

class OutreachMessage(models.Model):
    """
    Stores AI-generated sales outreach campaigns across multiple formats.
    Supports Cold Email, Follow-up Email, LinkedIn Message, Sales Call Script, and Meeting Request.
    """
    TYPE_COLD_EMAIL = 'cold_email'
    TYPE_FOLLOW_UP = 'follow_up'
    TYPE_LINKEDIN = 'linkedin'
    TYPE_CALL_SCRIPT = 'call_script'
    TYPE_MEETING_REQ = 'meeting_req'

    MESSAGE_TYPE_CHOICES = [
        (TYPE_COLD_EMAIL, 'Cold Email'),
        (TYPE_FOLLOW_UP, 'Follow-up Email'),
        (TYPE_LINKEDIN, 'LinkedIn Direct Message'),
        (TYPE_CALL_SCRIPT, 'Sales Call Script'),
        (TYPE_MEETING_REQ, 'Meeting Request'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outreach_messages')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='outreach_messages')
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPE_CHOICES, default=TYPE_COLD_EMAIL, db_index=True)
    target_role = models.CharField(max_length=255, default='Decision Maker / VP of Sales', help_text="Target Persona Role")
    subject = models.CharField(max_length=255, blank=True, help_text="Email Subject Line or Title")
    content = models.TextField(help_text="AI Generated Sales Content")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Outreach Message"
        verbose_name_plural = "Outreach Messages"

    def __str__(self):
        comp_name = self.company.name if self.company else "General Prospect"
        return f"{self.get_message_type_display()} for {comp_name} ({self.created_at.strftime('%Y-%m-%d')})"
