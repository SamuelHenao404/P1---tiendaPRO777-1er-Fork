from django.urls import path

from . import views

app_name = "items"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/", views.detail, name="detail"),
    path("browse/", views.browse, name="browse"),
    path("about/", views.about, name="about"),
]
