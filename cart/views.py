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

    # Integrar productos personalizados del carrito de la sesión
    personalizado_items = []
    total_personalizados = 0
    carrito_perso = request.session.get('carrito_personalizado', [])
    from personalizaciones.models import ProductoPersonalizado
    for it in carrito_perso:
        try:
            pp = ProductoPersonalizado.objects.get(id=it['pp_id'])
            cantidad = int(it['cantidad'])
            subtotal = pp.calcular_subtotal(cantidad)
            total_personalizados += float(subtotal)
            personalizado_items.append({
                'pp': pp,
                'cantidad': cantidad,
                'talla': it.get('talla'),
                'color': it.get('color'),
                'subtotal': subtotal
            })
        except Exception:
            continue

    total = summ + total_personalizados

    return render(
        request,
        "cart/cart.html",
        {
            "cart_items": cart_items,
            "personalizado_items": personalizado_items,
            "sum": total,
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
    carrito_perso = request.session.get('carrito_personalizado', [])
    from personalizaciones.models import ProductoPersonalizado

    if cart_items.count() == 0 and not carrito_perso:
        return redirect("cart:cart")

    receipt = PurchaseReceipt(buyer=request.user)
    receipt.save()
    total = 0

    # Procesar productos normales
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

    # Procesar productos personalizados
    for it in carrito_perso:
        try:
            pp = ProductoPersonalizado.objects.get(id=it['pp_id'])
            cantidad = int(it['cantidad'])
            subtotal = pp.calcular_subtotal(cantidad)
            total += float(subtotal)
            # Aquí podrías marcar el producto personalizado como comprado, cambiar estado, etc.
            # Ejemplo: pp.estado = 'comprado'; pp.save()
        except Exception:
            continue

    receipt.total = total
    receipt.save()
    cart.items.all().delete()
    # Limpiar carrito personalizado de la sesión
    request.session['carrito_personalizado'] = []
    request.session.modified = True
    return redirect("user_profile:purchases")
