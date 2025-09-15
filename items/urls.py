from django.urls import path
from .views import item_list, ItemDetailView, about, browse, pedido_recibo_pdf, pedidos_empresa

# Necesario para poder usar {% url 'items:...' %}
app_name = "items"

urlpatterns = [
    # Home / catálogo
    path("", item_list, name="index"),

    # Vista de pedidos para empresas
    path("empresa/pedidos/", pedidos_empresa, name="pedidos_empresa"),

    # Recibo PDF de pedido
    path("pedido/<int:pedido_id>/recibo/", pedido_recibo_pdf, name="pedido_recibo_pdf"),

    # Detalle de producto
    path("items/<int:pk>/", ItemDetailView.as_view(), name="item_detail"),
    path("item/<int:pk>/", ItemDetailView.as_view(), name="detail"),

    # Páginas auxiliares usadas por el navbar del template base.html
    path("about/", about, name="about"),
    path("browse/", browse, name="browse"),
]
