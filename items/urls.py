from django.urls import path
from .views import item_list, ItemDetailView, about, browse

# Necesario para poder usar {% url 'items:...' %}
app_name = "items"

urlpatterns = [
    # Home / catálogo
    path("", item_list, name="index"),

    # Detalle de producto
    path("items/<int:pk>/", ItemDetailView.as_view(), name="item_detail"),
    path("item/<int:pk>/", ItemDetailView.as_view(), name="detail"),

    # Páginas auxiliares usadas por el navbar del template base.html
    path("about/", about, name="about"),
    path("browse/", browse, name="browse"),
]
