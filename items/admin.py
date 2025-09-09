from django.contrib import admin

from .models import Category, Item, PurchaseReceipt

admin.site.register([Category, Item, PurchaseReceipt])
