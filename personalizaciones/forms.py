from django import forms
from django.apps import apps
from .models import Diseno, PRODUCTO_MODEL_PATH

APP_LABEL, MODEL_NAME = PRODUCTO_MODEL_PATH.split('.')
Item = apps.get_model(APP_LABEL, MODEL_NAME)

TALLAS = [('S','S'), ('M','M'), ('L','L'), ('XL','XL')]
COLORES = [('blanco','Blanco'), ('negro','Negro'), ('azul','Azul'), ('rojo','Rojo')]
UBICACIONES = [
    ('pecho','Pecho'),
    ('espalda','Espalda'),
    ('manga_izquierda','Manga izquierda'),
    ('manga_derecha','Manga derecha'),
]

class FormularioPersonalizacion(forms.Form):
    producto = forms.ModelChoiceField(queryset=Item.objects.none(), label="Prenda base", required=False)
    talla = forms.ChoiceField(choices=TALLAS)
    color = forms.ChoiceField(choices=COLORES)
    cantidad = forms.IntegerField(min_value=1, initial=1)
    ubicacion_en_prenda = forms.ChoiceField(choices=UBICACIONES)
    imagen_diseno = forms.ImageField(label="Sube tu diseño (PNG/JPG)", required=False)

    def __init__(self, *args, **kwargs):
        producto_fijo = kwargs.pop('producto_fijo', None)
        super().__init__(*args, **kwargs)
        if producto_fijo is not None:
            self.fields['producto'].queryset = Item.objects.filter(pk=producto_fijo.pk)
            self.fields['producto'].initial = producto_fijo
            self.fields['producto'].widget = forms.HiddenInput()
        else:
            self.fields['producto'].queryset = Item.objects.all().order_by('id')
