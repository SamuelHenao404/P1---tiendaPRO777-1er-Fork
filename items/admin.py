from django.contrib import admin

from .models import Category, Item, PurchaseReceipt, PurchasedItem


class PurchasedItemInline(admin.TabularInline):
	model = PurchasedItem
	extra = 0
	fields = ('item', 'size', 'quantity')
	readonly_fields = ('item', 'size', 'quantity')
	can_delete = False
	show_change_link = False

class PurchaseReceiptAdmin(admin.ModelAdmin):
	inlines = [PurchasedItemInline]
	list_display = ('buyer', 'total', 'date')

admin.site.register(Category)
class ItemAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'price', 'stock', 'is_sold', 'is_on_sale')
	list_editable = ('stock',)

admin.site.register(Item, ItemAdmin)
admin.site.register(PurchaseReceipt, PurchaseReceiptAdmin)
