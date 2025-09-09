from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from items.models import Item, PurchaseReceipt
from django.views.decorators.http import require_POST


@login_required(login_url="login")
@require_POST
def add_to_cart(request, item_id):
    size = request.POST.get("size")
    if not size:
        return redirect("items:detail", item_id=item_id)
    if "cart_items" in request.session.keys():
        # Verifica que el item con la talla no se agregue dos veces
        if not any(
            ci["id"] == item_id and ci["size"] == size for ci in request.session["cart_items"]
        ):
            request.session["cart_items"].append({"id": item_id, "size": size})
    else:
        request.session["cart_items"] = [{"id": item_id, "size": size}]
    request.session.modified = True
    return redirect("cart:cart")


@login_required(login_url="login")
def remove_from_cart(request, item_id, size):
    if "cart_items" in request.session.keys():
        request.session["cart_items"] = [ci for ci in request.session["cart_items"] if not (str(ci["id"]) == str(item_id) and ci["size"] == size)]
        request.session.modified = True
    return redirect("cart:cart")


@login_required(login_url="login")
def cart(request):
    summ = 0
    cart_items = []
    if "cart_items" in request.session.keys():
        for cart_item in request.session["cart_items"]:
            item = Item.objects.get(pk=cart_item["id"])
            cart_items.append({"item": item, "size": cart_item["size"]})
            summ += item.discounted_price()
    return render(
        request,
        "cart/cart.html",
        {
            "cart_items": cart_items,
            "sum": summ,
        },
    )


@login_required(login_url="login")
def purchase(request):
    if len(request.session["cart_items"]) <= 0:
        return redirect("cart:cart")
    else:
        receipt = PurchaseReceipt(buyer=request.user)
        receipt.save()
        total = 0
        for item_id in request.session["cart_items"]:
            item = Item.objects.get(pk=item_id)
            receipt.items.add(item)
            total += item.discounted_price()
        receipt.total = total
        receipt.save()
        request.session.pop("cart_items")
        return redirect("user_profile:purchases")

print("hola")