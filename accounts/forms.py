from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'display_name', 'email', 'phone',
            'address', 'city', 'state', 'postal_code', 'country'
        ]
        labels = {
            'display_name': _('Display name'),
            'email': _('Email'),
            'phone': _('Phone'),
            'address': _('Address'),
            'city': _('City'),
            'state': _('State'),
            'postal_code': _('Postal code'),
            'country': _('Country'),
        }
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'w3-input'}),
            'email': forms.EmailInput(attrs={'class': 'w3-input'}),
            'phone': forms.TextInput(attrs={'class': 'w3-input'}),
            'address': forms.TextInput(attrs={'class': 'w3-input'}),
            'city': forms.TextInput(attrs={'class': 'w3-input'}),
            'state': forms.TextInput(attrs={'class': 'w3-input'}),
            'postal_code': forms.TextInput(attrs={'class': 'w3-input'}),
            'country': forms.TextInput(attrs={'class': 'w3-input'}),
        }