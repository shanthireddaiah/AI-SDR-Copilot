from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    """
    Form for user registration.
    Extends Django's UserCreationForm with styled light Bootstrap form fields.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-saas',
            'placeholder': 'name@company.com'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply light-themed SaaS Bootstrap classes to all input fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control form-control-saas',
                'placeholder': f"Enter {field.label.lower() if field.label else field_name}"
            })
