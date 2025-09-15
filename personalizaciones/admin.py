from django.contrib import admin
from .models import Diseno, ProductoPersonalizado, PlantillaBase

@admin.register(Diseno)
class DisenoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'ubicacion_en_prenda', 'generado_por', 'creado_en')
    list_filter = ('generado_por', 'creado_en')
    search_fields = ('usuario__username',)

@admin.register(ProductoPersonalizado)
class ProductoPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'diseno', 'ubicacion_en_prenda', 'precio_adicional', 'creado_en')
    list_filter = ('ubicacion_en_prenda', 'creado_en')
    search_fields = ('producto__id', 'diseno__id')
    raw_id_fields = ('producto', 'diseno')  # dejamos raw_id para evitar errores con autocomplete

@admin.register(PlantillaBase)
class PlantillaBaseAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'color')
    list_filter = ('tipo', 'color')
    search_fields = ('tipo', 'color')
