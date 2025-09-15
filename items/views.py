from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Pedido
# Vista para empresas: mostrar pedidos asignados
@login_required(login_url="login")
def pedidos_empresa(request):
    if not hasattr(request.user, 'empresa'):
        return render(request, "items/no_access.html")
    estado = request.GET.get('estado')
    pedidos = Pedido.objects.filter(empresa_encargada=request.user.empresa)
    if estado:
        pedidos = pedidos.filter(estado=estado)

    # Cambiar estado de pedido (POST)
    if request.method == "POST":
        pedido_id = request.POST.get('pedido_id')
        nuevo_estado = request.POST.get('nuevo_estado')
        pedido = get_object_or_404(Pedido, id=pedido_id, empresa_encargada=request.user.empresa)
        if nuevo_estado in dict(Pedido.ESTADO_CHOICES):
            pedido.estado = nuevo_estado
            pedido.save()
        return redirect(request.path + f'?estado={estado}' if estado else request.path)

    return render(request, "items/pedidos_empresa.html", {"pedidos": pedidos, "estado": estado, "estados": Pedido.ESTADO_CHOICES})
from django.http import FileResponse, Http404
from .models import Pedido
# Vista para servir el PDF del pedido
def pedido_recibo_pdf(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id, nombre_cliente=request.user.nombre)
        if not pedido.recibo_pdf:
            raise Http404("Recibo no encontrado")
        return FileResponse(pedido.recibo_pdf.open('rb'), content_type='application/pdf')
    except Pedido.DoesNotExist:
        raise Http404("Pedido no encontrado")
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator
from django.db.models import Case, When, Value, CharField

from .models import Category, Item
from personalizaciones.models import PlantillaBase

# ---------- Listado (home del catálogo) ----------
def item_list(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'cliente':
            items = Item.objects.all().order_by("id")
            return render(request, "items/index.html", {"items": items})
        elif hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'empresa':
            # Redirigir a dashboard de empresa (ajusta la URL según tu app)
            return render(request, "items/empresa_dashboard.html")
        elif hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'administrador':
            # Redirigir a dashboard de admin (ajusta la URL según tu app)
            return render(request, "items/admin_dashboard.html")
        else:
            return render(request, "items/no_access.html")
    else:
        # Usuario no autenticado: puedes mostrar home público o redirigir al login
        return render(request, "items/index.html", {"items": []})

# ---------- Utilidad para deducir el tipo desde el título ----------
def _infer_tipo_from_title(title: str) -> str:
    t = (title or "").lower()
    if "hoodie" in t:
        return "hoodie"
    if "camibuso" in t or "long-sleeve" in t or "long sleeve" in t:
        return "camibuso" 
    return "camiseta"

# ---------- Detalle con plantillas (colores desde admin) ----------
class ItemDetailView(DetailView):
    model = Item
    template_name = "items/item_detail.html"
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        item = ctx["item"]
        tipo = _infer_tipo_from_title(getattr(item, "title", ""))
        ctx["plantillas"] = PlantillaBase.objects.filter(tipo=tipo).order_by("color")
        return ctx

# ---------- Páginas auxiliares que pide el navbar ----------
def about(request):
    return render(request, "items/about.html", {})  # template simple

def browse(request):
    # Obtener todos los items disponibles
    items = Item.objects.all()
    
    # Obtener todas las categorías para el filtro
    categories = Category.objects.all()
    
    # Filtro por búsqueda de texto
    query = request.GET.get('query', '').strip()
    if query:
        items = items.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Filtro por categoría
    category_id = request.GET.get('category')
    if category_id:
        try:
            category_id = int(category_id)
            items = items.filter(category_id=category_id)
        except (ValueError, TypeError):
            pass
    
    # Filtro por rango de precios
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        try:
            min_price = float(min_price)
            items = items.filter(price__gte=min_price)
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            max_price = float(max_price)
            items = items.filter(price__lte=max_price)
        except (ValueError, TypeError):
            pass
    
    # Filtro solo en stock
    if request.GET.get('in_stock_only'):
        items = items.filter(stock__gt=0)
    
    # Filtro solo en oferta
    if request.GET.get('on_sale_only'):
        items = items.filter(is_on_sale=True)
    
    # Ordenamiento
    sort_by = request.GET.get('sort', 'title')
    valid_sorts = ['title', '-title', 'price', '-price', 'created_at', '-created_at']
    
    if sort_by in valid_sorts:
        items = items.order_by(sort_by)
    else:
        items = items.order_by('title')
    
    # Paginación
    paginator = Paginator(items, 12)  # 12 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'items': page_obj,
        'categories': categories,
        'query': query,
        'category_id': int(category_id) if category_id else None,
    }
    
    return render(request, "items/browse.html", context)
