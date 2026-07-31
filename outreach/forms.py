from django import forms
from .models import OutreachMessage
from research.models import Company

class OutreachForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Company.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select a target company from your research history (Optional)"
    )
    company_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Acme Corp'}),
        help_text="Or enter company name manually"
    )
    message_type = forms.ChoiceField(
        choices=OutreachMessage.MESSAGE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial=OutreachMessage.TYPE_COLD_EMAIL
    )
    target_role = forms.CharField(
        max_length=255,
        required=False,
        initial="VP of Sales / Decision Maker",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Chief Technology Officer'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['company'].queryset = Company.objects.filter(user=user)
