# shop/urls.py
from django.urls import path
from .views import (
    ProductListView, ProductDetailView,
    cart_view, cart_add, cart_remove,
    checkout, order_success,
)

app_name = "shop"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("category/<slug:slug>/", ProductListView.as_view(), name="category"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),

    path("cart/", cart_view, name="cart"),
    path("cart/add/<int:product_id>/", cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", cart_remove, name="cart_remove"),

    path("checkout/", checkout, name="checkout"),
    path("order/success/", order_success, name="order_success"),
]
