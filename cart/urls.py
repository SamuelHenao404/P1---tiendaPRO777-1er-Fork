from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart, name="cart"),
    path("add-item-<int:item_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove-item-<int:item_id>/<str:size>/", views.remove_from_cart, name="remove_from_cart"),
    path("purchase/", views.purchase, name="purchase"),
]
