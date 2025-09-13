from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    # parent = models.OneToOneField("Category", on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Item(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to="item_images", blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    discount = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="items"
    )
    stock = models.IntegerField(default=0)

    class Meta:
        ordering = ("title",)

    def __str__(self) -> str:
        return f"{self.title} | {self.category} | ${self.price}"

    def discounted_price(self):
        return self.price - self.price * self.discount


class PurchaseReceipt(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.buyer.username} | {self.total} | {self.date}"

    def receipt_items(self):
        return list(self.purchased_items.all())


class PurchasedItem(models.Model):
    receipt = models.ForeignKey(PurchaseReceipt, on_delete=models.CASCADE, related_name="purchased_items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    size = models.CharField(max_length=20, blank=True, null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.item.title} | Talla: {self.size} | Cantidad: {self.quantity}"
