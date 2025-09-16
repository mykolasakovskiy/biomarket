from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_home, name="home"),
    path("add/<slug:slug>/", views.add_to_cart, name="add"),
]
