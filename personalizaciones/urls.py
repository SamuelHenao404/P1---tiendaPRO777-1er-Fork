from django.urls import path
from . import views

urlpatterns = [
    path("personalizar/", views.personalizar, name="personalizar"),
    path("carrito/", views.carrito_personalizado, name="carrito_personalizado"),
    path("carrito/eliminar/<int:index>/", views.carrito_eliminar, name="carrito_eliminar"),
    path("personalizar/<int:producto_id>/", views.personalizar, name="personalizar_producto"),
]
