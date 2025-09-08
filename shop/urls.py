from django.urls import path
from .views import ProductListView, ProductDetailView
from .cart_views import cart

app_name = "shop"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("category/<slug:slug>/", ProductListView.as_view(), name="category"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path("cart/", cart, name="cart"),
]
