from django import forms
from .models import Company

class CompanyResearchForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'website', 'industry', 'user_description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-saas', 'placeholder': 'e.g. Stripe, Acme Corp'}),
            'website': forms.URLInput(attrs={'class': 'form-control form-control-saas', 'placeholder': 'https://example.com'}),
            'industry': forms.TextInput(attrs={'class': 'form-control form-control-saas', 'placeholder': 'e.g. FinTech, B2B SaaS'}),
            'user_description': forms.Textarea(attrs={'class': 'form-control form-control-saas', 'rows': 3, 'placeholder': 'Enter background notes, target products, or market positioning...'}),
        }
