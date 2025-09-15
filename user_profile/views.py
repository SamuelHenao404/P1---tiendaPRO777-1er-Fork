from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from .forms import EditProfileForm, CustomPasswordChangeForm
from items.models import PurchaseReceipt, Pedido


@login_required(login_url="login")
def user_profile(request):
    return render(request, "user_profile/profile.html")


@login_required(login_url="login")
def purchase_history(request):
    receipts = list(PurchaseReceipt.objects.filter(buyer=request.user))
    pedidos = list(Pedido.objects.filter(nombre_cliente=request.user.nombre))
    return render(
        request,
        "user_profile/purchase_history.html",
        {
            "receipts": receipts,
            "pedidos": pedidos,
        },
    )


@login_required(login_url="login")
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("user_profile:user_profile")
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, "user_profile/edit_profile.html", {"form": form})


@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Contraseña cambiada correctamente.")
            return redirect("user_profile:user_profile")
        else:
            messages.error(request, "Por favor corrige los errores.")
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, "user_profile/change_password.html", {"form": form})
