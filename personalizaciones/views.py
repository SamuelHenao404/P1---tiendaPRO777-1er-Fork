from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.apps import apps
from .forms import FormularioPersonalizacion
from .models import Diseno, ProductoPersonalizado, PRODUCTO_MODEL_PATH

APP_LABEL, MODEL_NAME = PRODUCTO_MODEL_PATH.split('.')
Producto = apps.get_model(APP_LABEL, MODEL_NAME)

@login_required
def personalizar(request, producto_id=None):
    if request.method == 'POST':
        form = FormularioPersonalizacion(request.POST, request.FILES)
        if form.is_valid():
            if producto_id:
                producto = get_object_or_404(Producto, pk=producto_id)
            else:
                producto = form.cleaned_data['producto']
            talla = form.cleaned_data['talla']
            color = form.cleaned_data['color']
            cantidad = form.cleaned_data['cantidad']
            ubicacion = form.cleaned_data['ubicacion_en_prenda']
            imagen = form.cleaned_data.get('imagen_diseno', None)

            diseno = Diseno.objects.create(
                usuario=request.user,
                ubicacion_en_prenda=ubicacion,
                generado_por='usuario'
            )
            if imagen:
                diseno.imagen_original = imagen
                diseno.save()
            perso = ProductoPersonalizado.objects.create(
                producto=producto,
                diseno=diseno,
                ubicacion_en_prenda=ubicacion,
                precio_adicional=0
            )
            perso.generar_preview()

            carrito = request.session.get('carrito_personalizado', [])
            carrito.append({'pp_id': perso.id, 'cantidad': int(cantidad), 'talla': talla, 'color': color})
            request.session['carrito_personalizado'] = carrito
            request.session.modified = True

            messages.success(request, "Producto personalizado añadido al carrito.")
            return redirect('carrito_personalizado')
    else:
        form = FormularioPersonalizacion(initial={'producto': producto_id} if producto_id else None)

    return render(request, 'personalizaciones/personalizar.html', {'form': form})

@login_required
def carrito_personalizado(request):
    # Redirige al carrito principal
    from django.urls import reverse
    return redirect(reverse('cart:cart'))

@login_required
def carrito_eliminar(request, index):
    carrito = request.session.get('carrito_personalizado', [])
    if 0 <= index < len(carrito):
        nuevo, i = [], 0
        while i < len(carrito):
            if i != index:
                nuevo.append(carrito[i])
            i = i + 1
        request.session['carrito_personalizado'] = nuevo
        request.session.modified = True
        messages.info(request, "Ítem eliminado del carrito.")
    return redirect('carrito_personalizado')
