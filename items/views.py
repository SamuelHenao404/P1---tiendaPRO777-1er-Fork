from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.views.generic.detail import DetailView

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
    if "long-sleeve" in t or "long sleeve" in t:
        return "camibuzo"
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
    # Puedes personalizar esta página; por ahora reusa el listado
    return item_list(request)
