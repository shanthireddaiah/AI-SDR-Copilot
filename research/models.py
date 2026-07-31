from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    """
    Stores target company information submitted by users and the AI-generated research summary.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies', db_index=True)
    
    # Manual User Inputs
    name = models.CharField(max_length=255, db_index=True, help_text="Target Company Name")
    website = models.URLField(max_length=500, blank=True, null=True, help_text="Company Website URL")
    industry = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="Industry Category")
    user_description = models.TextField(blank=True, null=True, help_text="User provided business description")

    # AI-Generated Research Output
    overview = models.TextField(blank=True, null=True, help_text="AI Business Overview")
    products = models.TextField(blank=True, null=True, help_text="AI Extracted Products & Services")
    pain_points = models.TextField(blank=True, null=True, help_text="Possible Customer Pain Points")
    sales_insights = models.TextField(blank=True, null=True, help_text="AI Generated Sales Insights")

    # AI-Generated Outreach Messages (Legacy / Quick Cache)
    email_outreach = models.TextField(blank=True, null=True, help_text="Personalized Email Draft")
    linkedin_outreach = models.TextField(blank=True, null=True, help_text="LinkedIn Direct Message Draft")
    cold_call_script = models.TextField(blank=True, null=True, help_text="Cold Outreach Call Pitch")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name
