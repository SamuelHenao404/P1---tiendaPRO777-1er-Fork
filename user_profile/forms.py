from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class CustomPasswordChangeForm(PasswordChangeForm):
    pass
