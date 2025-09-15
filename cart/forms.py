from django import forms

class DireccionEnvioForm(forms.Form):
    direccion_envio = forms.CharField(label="Dirección de envío", max_length=255, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Dirección de envío"}))
