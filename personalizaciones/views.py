from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.apps import apps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .forms import FormularioPersonalizacion
from .models import Diseno, ProductoPersonalizado, PRODUCTO_MODEL_PATH
from items.models import Item

APP_LABEL, MODEL_NAME = PRODUCTO_MODEL_PATH.split('.')
Producto = apps.get_model(APP_LABEL, MODEL_NAME)

@login_required
def personalizar(request, producto_id=None):
    print(f"DEBUG: Iniciando personalización para producto_id: {producto_id}")  # Debug log
    
    if request.method == 'POST':
        print(f"DEBUG: Método POST recibido")  # Debug log
        form = FormularioPersonalizacion(request.POST, request.FILES)
        print(f"DEBUG: Formulario creado, válido: {form.is_valid()}")  # Debug log
        
        if form.is_valid():
            print(f"DEBUG: Formulario es válido, procesando...")  # Debug log
            if producto_id:
                producto = get_object_or_404(Producto, pk=producto_id)
            else:
                producto = form.cleaned_data['producto']
            talla = form.cleaned_data['talla']
            color = form.cleaned_data['color']
            cantidad = form.cleaned_data['cantidad']
            ubicacion = form.cleaned_data['ubicacion_en_prenda']
            
            # Obtener los nuevos campos del formulario
            tamaño_imagen = form.cleaned_data.get('tamaño_imagen', 0.3)
            posicion_x = form.cleaned_data.get('posicion_x', 0.5)
            posicion_y = form.cleaned_data.get('posicion_y', 0.35)
            # Obtener tipo_diseno directamente del POST ya que usamos HTML estático
            tipo_diseno = request.POST.get('tipo_diseno', 'imagen')
            print(f"DEBUG: tipo_diseno obtenido del POST: {tipo_diseno}")  # Debug log
            prompt_ia = form.cleaned_data.get('prompt_ia', '')
            
            # Crear el diseño
            diseno = Diseno.objects.create(
                usuario=request.user,
                ubicacion_en_prenda=ubicacion,
                generado_por='usuario',
                tamaño_imagen=tamaño_imagen,
                posicion_x=posicion_x,
                posicion_y=posicion_y
            )
            
            # Procesar según el tipo de diseño
            if tipo_diseno == 'imagen':
                # Diseño con imagen propia
                imagen = form.cleaned_data.get('imagen_diseno', None)
                if imagen:
                    diseno.imagen_original = imagen
                    diseno.save()
            elif tipo_diseno == 'ia':
                # FUNCIONALIDAD DESHABILITADA - Diseño generado por IA
                messages.error(request, "La funcionalidad de generación de diseños con IA ha sido deshabilitada.")
                return redirect('cart:cart')
            
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
            
            print(f"DEBUG: Producto personalizado creado: {perso.id}")  # Debug log
            print(f"DEBUG: Carrito actualizado: {carrito}")  # Debug log

            messages.success(request, "Producto personalizado añadido al carrito.")
            return redirect('cart:cart')
        else:
            print(f"DEBUG: Formulario NO es válido, errores: {form.errors}")  # Debug log
    else:
        print(f"DEBUG: Método GET, creando formulario inicial")  # Debug log
        form = FormularioPersonalizacion(initial={'producto': producto_id} if producto_id else None)

    # Obtener el item para el template
    if producto_id:
        item = get_object_or_404(Item, pk=producto_id)
    else:
        item = None
    
    return render(request, 'items/item_detail.html', {'form': form, 'item': item})

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

# FUNCIÓN DESHABILITADA - Generación de diseños con IA eliminada
# @login_required
# @require_POST
# def generar_diseno_ia(request):
#     """
#     Vista AJAX para generar diseños con IA - DESHABILITADA
#     """
#     return JsonResponse({
#         'success': False,
#         'error': 'La funcionalidad de generación de diseños con IA ha sido deshabilitada'
#     })
