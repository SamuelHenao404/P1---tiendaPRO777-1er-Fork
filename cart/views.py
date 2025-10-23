from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from items.models import Item, PurchaseReceipt, PurchasedItem
from .forms import DireccionEnvioForm
from .models import Cart, CartItem
from django.views.decorators.http import require_POST
from personalizaciones.models import PlantillaBase

@login_required(login_url="login")
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('item').all()
    summ = sum(ci.item.discounted_price() * ci.quantity for ci in cart_items)

    # Integrar productos personalizados del carrito de la sesión
    personalizado_items = []
    total_personalizados = 0
    carrito_perso = request.session.get('carrito_personalizado', [])
    print(f"DEBUG: Carrito personalizado en sesión: {carrito_perso}")  # Debug log
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
            print(f"DEBUG: Producto personalizado agregado: {pp.id}")  # Debug log
        except Exception as e:
            print(f"DEBUG: Error procesando producto personalizado {it.get('pp_id', 'N/A')}: {e}")  # Debug log
            continue

    total = summ + total_personalizados

    return render(
        request,
        "cart/cart.html",
        {
            "cart_items": cart_items,
            "personalizado_items": personalizado_items,
            "sum": total,
            "debug_carrito": carrito_perso,  # Para depuración
            "debug_count": len(personalizado_items),  # Para depuración
        },
    )

@login_required(login_url="login")
@require_POST
def add_to_cart(request, item_id):
    size = request.POST.get("size")
    color = request.POST.get("color")
    cantidad = request.POST.get("cantidad")
    imagen_diseno = request.FILES.get("imagen_diseno")
    if not size:
        return redirect("items:item_detail", pk=item_id)
    item = Item.objects.get(pk=item_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item, size=size)
    if color:
        cart_item.color = color
    if cantidad:
        cart_item.quantity = int(cantidad)
    if imagen_diseno:
        cart_item.imagen_diseno = imagen_diseno
    if not created and not cantidad:
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
def remove_personalized_item(request, pp_id):
    """Eliminar un producto personalizado del carrito"""
    carrito_perso = request.session.get('carrito_personalizado', [])
    
    # Buscar y eliminar el producto personalizado
    carrito_perso = [item for item in carrito_perso if item.get('pp_id') != pp_id]
    
    # Actualizar la sesión
    request.session['carrito_personalizado'] = carrito_perso
    
    return redirect("cart:cart")


@login_required(login_url="login")
def purchase(request):

    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.select_related('item').all()
    carrito_perso = request.session.get('carrito_personalizado', [])
    from personalizaciones.models import ProductoPersonalizado

    if cart_items.count() == 0 and not carrito_perso:
        return redirect("cart:cart")

    if request.method == "POST":
        form = DireccionEnvioForm(request.POST)
        if form.is_valid():
            direccion_envio = form.cleaned_data['direccion_envio']
            # --- CREAR PEDIDO ---
            from items.models import Pedido, PedidoItem
            from core.models import Empresa
            import random

            nombre_cliente = request.user.nombre if hasattr(request.user, 'nombre') else str(request.user)
            pedido = Pedido.objects.create(
                nombre_cliente=nombre_cliente,
                direccion_envio=direccion_envio,
            )
            pedido.asignar_empresa_aleatoria()

            total = 0
            for cart_item in cart_items:
                PedidoItem.objects.create(
                    pedido=pedido,
                    item=cart_item.item,
                    cantidad=cart_item.quantity
                )
                total += cart_item.item.discounted_price() * cart_item.quantity
                item_obj = cart_item.item
                item_obj.stock -= cart_item.quantity
                if item_obj.stock <= 0:
                    item_obj.stock = 0
                    item_obj.is_sold = True
                item_obj.save()

            # (Opcional) Mantener PurchaseReceipt para compatibilidad
            receipt = PurchaseReceipt(buyer=request.user)
            receipt.save()
            for cart_item in cart_items:
                PurchasedItem.objects.create(
                    receipt=receipt,
                    item=cart_item.item,
                    size=cart_item.size,
                    quantity=cart_item.quantity
                )

            # Procesar productos personalizados (mantener lógica existente)
            for it in carrito_perso:
                try:
                    pp = ProductoPersonalizado.objects.get(id=it['pp_id'])
                    cantidad = int(it['cantidad'])
                    subtotal = pp.calcular_subtotal(cantidad)
                    total += float(subtotal)
                except Exception:
                    continue

            receipt.total = total
            receipt.save()
            # Generar y guardar el PDF del recibo
            from items.utils import generar_recibo_pdf
            recibo_pdf = generar_recibo_pdf(pedido)
            pedido.recibo_pdf.save(recibo_pdf.name, recibo_pdf)
            pedido.save()
            cart.items.all().delete()
            request.session['carrito_personalizado'] = []
            request.session.modified = True
            # Redirigir a la descarga del PDF en una nueva pestaña y luego al historial
            return render(request, "cart/compra_exitosa.html", {"pedido": pedido})
        else:
            # Si el formulario no es válido, mostrar errores
            return render(request, "cart/checkout.html", {"form": form, "cart_items": cart_items})
    else:
        form = DireccionEnvioForm()
        return render(request, "cart/checkout.html", {"form": form, "cart_items": cart_items})


    # --- CREAR PEDIDO ---
    from items.models import Pedido, PedidoItem
    from core.models import Empresa
    import random

    # Obtener dirección de envío (puedes pedirla en un formulario, aquí ejemplo simple)
    direccion_envio = getattr(request.user, 'direccion', 'Sin dirección')
    nombre_cliente = request.user.nombre if hasattr(request.user, 'nombre') else str(request.user)

    pedido = Pedido.objects.create(
        nombre_cliente=nombre_cliente,
        direccion_envio=direccion_envio,
    )
    # Asignar empresa aleatoria
    pedido.asignar_empresa_aleatoria()

    total = 0
    # Procesar productos normales
    for cart_item in cart_items:
        PedidoItem.objects.create(
            pedido=pedido,
            item=cart_item.item,
            cantidad=cart_item.quantity
        )
        total += cart_item.item.discounted_price() * cart_item.quantity
        # Descontar stock
        item_obj = cart_item.item
        item_obj.stock -= cart_item.quantity
        if item_obj.stock <= 0:
            item_obj.stock = 0
            item_obj.is_sold = True
        item_obj.save()

    # --- FIN CREAR PEDIDO ---

    # (Opcional) Mantener PurchaseReceipt para compatibilidad
    receipt = PurchaseReceipt(buyer=request.user)
    receipt.save()
    for cart_item in cart_items:
        PurchasedItem.objects.create(
            receipt=receipt,
            item=cart_item.item,
            size=cart_item.size,
            quantity=cart_item.quantity
        )

    # Procesar productos personalizados (mantener lógica existente)

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
    pedido.save()
    cart.items.all().delete()
    # Limpiar carrito personalizado de la sesión
    request.session['carrito_personalizado'] = []
    request.session.modified = True
    return redirect("user_profile:purchases")

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    tipo = item.category.lower()
    plantillas = PlantillaBase.objects.filter(tipo=tipo)

    return render(request, "items/item_detail.html", {
        "item": item,
        "plantillas": plantillas,
        # ...otros context...
    })
