from django.urls import path
from .views import ProductListView, ProductDetailView  # підлаштуй, якщо імена інші
from . import views  # якщо є функціональні в’юшки (наприклад, cart)

app_name = "shop"

urlpatterns = [
    # головна: список товарів
    path("", ProductListView.as_view(), name="product_list"),

    # фільтр за категорією (якщо використовуєш)
    path("category/<slug:slug>/", ProductListView.as_view(), name="category"),

    # детальна сторінка товару (підлаштуй під свою в’юшку/шлях)
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),

    # кошик (якщо є; інакше тимчасово прибери кнопку у base.html)
    path("cart/", views.cart, name="cart"),
]
