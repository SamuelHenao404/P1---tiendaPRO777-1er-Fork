from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Empresa

class RegisterUserForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)
    direccion = forms.CharField(label="Dirección de la empresa", max_length=255, required=False)

    class Meta:
        model = Usuario
        fields = ("nombre", "correo", "tipo_usuario")
        widgets = {
            'tipo_usuario': forms.Select(choices=Usuario.TIPO_USUARIO_CHOICES)
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get("tipo_usuario")
        direccion = cleaned_data.get("direccion")
        if tipo_usuario == "empresa" and not direccion:
            self.add_error("direccion", "La dirección es obligatoria para empresas.")
        return cleaned_data

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            # Si es empresa, crear el objeto Empresa
            if self.cleaned_data.get("tipo_usuario") == "empresa":
                Empresa.objects.create(usuario=user, direccion=self.cleaned_data["direccion"])
        return user
