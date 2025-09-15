from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator
from django.db.models import Case, When, Value, CharField

from .models import Category, Item
from personalizaciones.models import PlantillaBase

# ---------- Listado (home del catálogo) ----------
def item_list(request):
    items = Item.objects.all().order_by("id")
    return render(request, "items/index.html", {"items": items})

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
