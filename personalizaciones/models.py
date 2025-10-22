from django.db import models
from django.conf import settings
import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from decimal import Decimal

# Path al modelo de producto real de tu proyecto
# En tu caso, apunta a Item del app "items"
PRODUCTO_MODEL_PATH = 'items.Item'


# ----------------- DISEÑO -----------------
class Diseno(models.Model):
    GENERADO_CHOICES = [('usuario', 'Usuario'), ('ia', 'IA')]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='disenos'
    )
    imagen_original = models.ImageField(upload_to='disenos/originales/')
    imagen_formateada = models.ImageField(upload_to='disenos/formateados/', blank=True, null=True)
    ubicacion_en_prenda = models.CharField(max_length=100, help_text="Ej: pecho, espalda, manga_izquierda, manga_derecha")
    generado_por = models.CharField(max_length=10, choices=GENERADO_CHOICES, default='usuario')
    
    # Nuevos campos para control de tamaño y posición
    tamaño_imagen = models.FloatField(default=0.3, help_text="Tamaño de la imagen como porcentaje del ancho de la prenda (0.1 a 1.0)")
    posicion_x = models.FloatField(default=0.5, help_text="Posición X como porcentaje del ancho de la prenda (0.0 a 1.0)")
    posicion_y = models.FloatField(default=0.35, help_text="Posición Y como porcentaje de la altura de la prenda (0.0 a 1.0)")
    
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diseño {self.id} ({self.generado_por})"


# ----------------- PRODUCTO PERSONALIZADO -----------------
def _infer_tipo_from_title(title: str) -> str:
    t = (title or '').lower()
    if 'hoodie' in t:
        return 'hoodie'
    if 'camibuso' in t or 'long-sleeve' in t or 'long sleeve' in t:
        return 'camibuso'
    return 'camiseta'

PRICE_FIELDS = ('precio_base', 'price', 'unit_price', 'base_price')

class ProductoPersonalizado(models.Model):
    producto = models.ForeignKey(
        PRODUCTO_MODEL_PATH,
        on_delete=models.CASCADE,
        related_name='personalizaciones'
    )
    diseno = models.ForeignKey(Diseno, on_delete=models.CASCADE, related_name='personalizaciones')
    ubicacion_en_prenda = models.CharField(max_length=100, help_text="pecho/espalda/manga_izquierda/manga_derecha")
    color = models.CharField(max_length=30, default='negro')
    imagen_visualizacion = models.ImageField(upload_to='previews/', blank=True, null=True)
    precio_adicional = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['producto']), models.Index(fields=['diseno'])]
        verbose_name = "Producto personalizado"
        verbose_name_plural = "Productos personalizados"

    def __str__(self):
        return f"Perso-{self.id} • prod={self.producto_id} • diseno={self.diseno_id}"

    @property
    def precio_unitario(self):
        base = None
        for fname in PRICE_FIELDS:
            if hasattr(self.producto, fname):
                base = getattr(self.producto, fname)
                break
        try:
            base = Decimal(str(base))
        except Exception:
            base = Decimal('0')
        extra = Decimal(str(self.precio_adicional or 0))
        return base + extra

    def calcular_subtotal(self, cantidad=1):
        if not cantidad or cantidad < 1:
            cantidad = 1
        return self.precio_unitario * Decimal(str(cantidad))

    def generar_preview(self):
        """
        Usa PlantillaBase(tipo inferido y self.color).
        Si no hay plantilla, usa lienzo blanco.
        """
        try:
            from .models import PlantillaBase  # import local para evitar dependencias circulares

            # tipo desde título del producto
            titulo = getattr(self.producto, 'title', '')
            tipo = _infer_tipo_from_title(titulo)
            color = (self.color or 'blanco').lower()

            plantilla = PlantillaBase.objects.filter(tipo=tipo, color=color).first()

            if plantilla:
                base = Image.open(plantilla.imagen_base.path).convert('RGBA')
            else:
                ruta_base = os.path.join(settings.MEDIA_ROOT, 'bases', f'{tipo}_{color}.png')
                if os.path.exists(ruta_base):
                    base = Image.open(ruta_base).convert('RGBA')
                else:
                    base = Image.new('RGBA', (1000, 1200), (255, 255, 255, 255))

            ruta_diseno = self.diseno.imagen_formateada.path if self.diseno.imagen_formateada else self.diseno.imagen_original.path
            logo = Image.open(ruta_diseno).convert('RGBA')

            # Usar los nuevos campos de tamaño y posición del diseño
            tamaño_imagen = getattr(self.diseno, 'tamaño_imagen', 0.3)
            posicion_x = getattr(self.diseno, 'posicion_x', 0.5)
            posicion_y = getattr(self.diseno, 'posicion_y', 0.35)
            
            # Limitar el tamaño entre 0.1 y 1.0
            tamaño_imagen = max(0.1, min(1.0, tamaño_imagen))
            
            ancho_objetivo = int(base.width * tamaño_imagen)
            ratio = ancho_objetivo / logo.width
            logo = logo.resize((ancho_objetivo, int(logo.height * ratio)), Image.LANCZOS)

            # Calcular posición basada en los porcentajes guardados
            x = int(base.width * posicion_x - logo.width / 2)
            y = int(base.height * posicion_y - logo.height / 2)
            
            # Asegurar que la imagen no se salga de los límites
            x = max(0, min(x, base.width - logo.width))
            y = max(0, min(y, base.height - logo.height))

            base.alpha_composite(logo, (x, y))

            buffer = BytesIO()
            base.convert('RGB').save(buffer, format='JPEG', quality=90)
            nombre_archivo = f"preview_{self.id or 'tmp'}.jpg"
            self.imagen_visualizacion.save(nombre_archivo, ContentFile(buffer.getvalue()), save=True)
        except Exception:
            if not self.imagen_visualizacion:
                self.imagen_visualizacion = self.diseno.imagen_original
                self.save(update_fields=['imagen_visualizacion'])
        return self.imagen_visualizacion


# ----------------- PLANTILLA BASE -----------------
class PlantillaBase(models.Model):
    class Tipo(models.TextChoices):
        CAMISETA = 'camiseta', 'Camiseta'
        CAMIBUSO = 'camibuso', 'Camibuso'
        HOODIE   = 'hoodie',   'Hoodie'

    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    color = models.CharField(max_length=30)  # ej: blanco, negro, azul, rojo
    imagen_base = models.ImageField(upload_to='bases/')  # PNG/JPG de la prenda base

    class Meta:
        unique_together = ('tipo', 'color')
        verbose_name = 'Plantilla base por color'
        verbose_name_plural = 'Plantillas base por color'

    def __str__(self):
        return f'{self.tipo} - {self.color}'
