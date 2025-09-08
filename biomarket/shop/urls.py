from django.urls import path
from . import views

app_name = "shop"
urlpatterns = [
    path('', views.ProductListView.as_view(), name='home'),
    path('category/<slug:slug>/', views.ProductListView.as_view(), name='category'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    path('checkout/', views.checkout, name='checkout'),
    path('payment/stripe/create/', views.stripe_create_checkout, name='stripe_create_checkout'),
    path('payment/stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('order/success/', views.order_success, name='order_success'),
]
