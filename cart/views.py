from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from items.models import Item, PurchaseReceipt, PurchasedItem
from .models import Cart, CartItem
from django.views.decorators.http import require_POST

@login_required(login_url="login")
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('item').all()
    summ = sum(ci.item.discounted_price() * ci.quantity for ci in cart_items)
    return render(
        request,
        "cart/cart.html",
        {
            "cart_items": cart_items,
            "sum": summ,
        },
    )

@login_required(login_url="login")
@require_POST
def add_to_cart(request, item_id):
    size = request.POST.get("size")
    if not size:
        return redirect("items:detail", item_id=item_id)
    item = Item.objects.get(pk=item_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item, size=size)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect("cart:cart")

@login_required(login_url="login")
def remove_from_cart(request, item_id, size):
    item = Item.objects.get(pk=item_id)
    cart = Cart.objects.get(user=request.user)
    CartItem.objects.filter(cart=cart, item=item, size=size).delete()
    return redirect("cart:cart")


@login_required(login_url="login")
def purchase(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.select_related('item').all()
    if cart_items.count() == 0:
        return redirect("cart:cart")
    receipt = PurchaseReceipt(buyer=request.user)
    receipt.save()
    total = 0
    for cart_item in cart_items:
        PurchasedItem.objects.create(
            receipt=receipt,
            item=cart_item.item,
            size=cart_item.size,
            quantity=cart_item.quantity
        )
        total += cart_item.item.discounted_price() * cart_item.quantity
        # Descontar stock
        item_obj = cart_item.item
        item_obj.stock -= cart_item.quantity
        if item_obj.stock <= 0:
            item_obj.stock = 0
            item_obj.is_sold = True
        item_obj.save()
    receipt.total = total
    receipt.save()
    cart.items.all().delete()
    return redirect("user_profile:purchases")
