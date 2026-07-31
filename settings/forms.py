from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['job_title', 'target_industry', 'preferred_tone', 'custom_openai_key']
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'target_industry': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_tone': forms.TextInput(attrs={'class': 'form-control'}),
            'custom_openai_key': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'sk-proj-... (Leave blank to use global env)'}, render_value=True),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
