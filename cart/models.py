from django.db import models
from django.conf import settings

from items.models import Item

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total = models.FloatField(default=0.0)

    def __str__(self):
        return f"Carrito de {self.user.nombre}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    size = models.CharField(max_length=10, default="M")
    color = models.CharField(max_length=20, blank=True, null=True)  # Nuevo campo
    quantity = models.PositiveIntegerField(default=1)               # Cambia a 'quantity' en vez de 'cantidad'
    imagen_diseno = models.ImageField(upload_to='cart/designs/', blank=True, null=True)  # Nuevo campo

    def __str__(self):
        return f"{self.item.title} x{self.quantity} ({self.size})"
