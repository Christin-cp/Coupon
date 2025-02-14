from django import forms
from .models import UserDetail

class UserForm(forms.ModelForm):
    class Meta:
        model = UserDetail
        fields = ['name', 'whatsapp_number', 'email']
