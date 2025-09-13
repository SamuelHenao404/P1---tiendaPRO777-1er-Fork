from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class RegisterUserForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre completo", max_length=150, required=True)

    class Meta:
        model = User
        fields = ("first_name", "username", "email", "password1", "password2")
