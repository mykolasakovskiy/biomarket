from decimal import Decimal

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from products.models import Product

from .models import Cart, CartItem


def cart_home(request: HttpRequest) -> HttpResponse:
    """Display cart contents using a template."""

    cart = _get_or_create_cart(request)
    cart_items = list(cart.items.select_related("product"))

    cart_total = Decimal("0.00")
    cart_quantity = 0

    for item in cart_items:
        line_total = item.product.price * item.quantity
        cart_total += line_total
        cart_quantity += item.quantity
        setattr(item, "line_total", line_total)

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "cart_total": cart_total,
        "cart_quantity": cart_quantity,
        "meta_title": "Кошик — Biomarket",
        "description": "Перевірте вміст вашого кошика Biomarket та завершіть оформлення замовлення.",
        "keywords": "Biomarket, кошик, замовлення, органічні продукти",
        "og_type": "website",
        "twitter_card": "summary",
    }

    return render(request, "cart/home.html", context)


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


@require_POST
def add_to_cart(request: HttpRequest, slug: str) -> HttpResponse:
    """Add the selected product to the active cart and redirect back."""

    product = get_object_or_404(Product, slug=slug)

    if product.stock <= 0:
        return redirect(
            request.POST.get("next")
            or request.GET.get("next")
            or product.get_absolute_url()
        )

    cart = _get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save(update_fields=["quantity"])

    redirect_url = (
        request.POST.get("next")
        or request.GET.get("next")
        or reverse("cart:home")
    )
    return redirect(redirect_url)
