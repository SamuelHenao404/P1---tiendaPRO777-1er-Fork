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
    
    # Nuevos campos para control de tamaño y posición
    tamaño_imagen = forms.FloatField(
        min_value=0.1, 
        max_value=1.0, 
        initial=0.3,
        label="Tamaño de la imagen",
        help_text="Tamaño como porcentaje del ancho de la prenda (10% a 100%)",
        widget=forms.NumberInput(attrs={'step': '0.05', 'min': '0.1', 'max': '1.0'})
    )
    posicion_x = forms.FloatField(
        min_value=0.0, 
        max_value=1.0, 
        initial=0.5,
        label="Posición horizontal",
        help_text="Posición horizontal como porcentaje (0% = izquierda, 100% = derecha)",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0.0', 'max': '1.0'})
    )
    posicion_y = forms.FloatField(
        min_value=0.0, 
        max_value=1.0, 
        initial=0.35,
        label="Posición vertical",
        help_text="Posición vertical como porcentaje (0% = arriba, 100% = abajo)",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0.0', 'max': '1.0'})
    )
    
    # Campo para prompt de IA
    prompt_ia = forms.CharField(
        max_length=500,
        required=False,
        label="Descripción para IA",
        help_text="Describe el diseño que quieres que la IA genere (ej: 'Un gato astronauta con colores azul y blanco')",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Ejemplo: Un diseño minimalista con mi nombre en tipografía elegante...',
            'class': 'form-control'
        })
    )
    
    # Campo para elegir entre imagen propia o IA - DESHABILITADO (usamos HTML estático)
    tipo_diseno = forms.ChoiceField(
        choices=[
            ('imagen', 'Subir mi propia imagen'),
            ('ia', 'Generar con IA')
        ],
        initial='imagen',
        label="Tipo de diseño",
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=False  # Cambiado a False porque usamos HTML estático
    )

    def __init__(self, *args, **kwargs):
        producto_fijo = kwargs.pop('producto_fijo', None)
        super().__init__(*args, **kwargs)
        if producto_fijo is not None:
            self.fields['producto'].queryset = Item.objects.filter(pk=producto_fijo.pk)
            self.fields['producto'].initial = producto_fijo
            self.fields['producto'].widget = forms.HiddenInput()
        else:
            self.fields['producto'].queryset = Item.objects.all().order_by('id')
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_diseno = cleaned_data.get('tipo_diseno')
        imagen_diseno = cleaned_data.get('imagen_diseno')
        prompt_ia = cleaned_data.get('prompt_ia')
        
        # Validar que se proporcione una imagen o un prompt de IA
        if tipo_diseno == 'imagen' and not imagen_diseno:
            raise forms.ValidationError("Debes subir una imagen cuando seleccionas 'Subir mi propia imagen'.")
        
        if tipo_diseno == 'ia' and not prompt_ia:
            raise forms.ValidationError("Debes describir el diseño cuando seleccionas 'Generar con IA'.")
        
        return cleaned_data
