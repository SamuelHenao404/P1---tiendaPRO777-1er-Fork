from django.urls import path
from . import views

app_name = "personalizaciones"

urlpatterns = [
    path("personalizar/", views.personalizar, name="personalizar"),
    path("carrito/", views.carrito_personalizado, name="carrito_personalizado"),
    path("carrito/eliminar/<int:index>/", views.carrito_eliminar, name="carrito_eliminar"),
    path("personalizar/<int:producto_id>/", views.personalizar, name="personalizar_producto"),
    path("generar-diseno-ia/", views.generar_diseno_ia, name="generar_diseno_ia"),
]
