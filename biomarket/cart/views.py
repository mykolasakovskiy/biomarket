from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from products.models import Product

from .models import Cart, CartItem


def cart_home(request: HttpRequest) -> HttpResponse:
    """Display a minimal placeholder cart page."""
    return HttpResponse("Cart is empty", content_type="text/plain")


def _get_or_create_cart(request: HttpRequest) -> Cart:
    """Return a cart linked to the current session or create a new one."""

    cart_id = request.session.get("cart_id")
    cart = Cart.objects.filter(pk=cart_id).first() if cart_id else None

    if request.user.is_authenticated:
        if cart and cart.user_id not in (None, request.user.id):
            cart = None
        if cart is None:
            cart, _created = Cart.objects.get_or_create(user=request.user)
        elif cart.user_id is None:
            cart.user = request.user
            cart.save(update_fields=["user"])
    else:
        if cart is None:
            cart = Cart.objects.create()

    request.session["cart_id"] = cart.pk
    return cart


def add_to_cart(request: HttpRequest, slug: str) -> HttpResponse:
    """Add the selected product to the active cart and redirect back."""

    product = get_object_or_404(Product, slug=slug)

    if product.stock <= 0:
        return redirect(request.GET.get("next") or product.get_absolute_url())

    cart = _get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save(update_fields=["quantity"])

    redirect_url = request.GET.get("next") or reverse("cart:home")
    return redirect(redirect_url)
