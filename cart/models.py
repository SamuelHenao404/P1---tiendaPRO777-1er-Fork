from django.db import models
from django.contrib.auth.models import User
from items.models import Item

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"Carrito de {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    size = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.item.title} x{self.quantity} ({self.size})"
