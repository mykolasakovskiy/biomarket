from decimal import Decimal

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

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
    """Return the active cart, merging session items into the user's cart if needed."""

    cart_id = request.session.get("cart_id")
    session_cart = Cart.objects.filter(pk=cart_id).first() if cart_id else None

    if request.user.is_authenticated:
        cart, _created = Cart.objects.get_or_create(user=request.user)

        if (
            session_cart
            and session_cart.pk != cart.pk
            and session_cart.user_id in (None, request.user.id)
        ):
            for item in session_cart.items.all():
                destination_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=item.product,
                    defaults={"quantity": item.quantity},
                )
                if not created:
                    destination_item.quantity += item.quantity
                    destination_item.save(update_fields=["quantity"])

            if session_cart.user_id is None:
                session_cart.delete()
    else:
        if session_cart is None or session_cart.user_id is not None:
            cart = Cart.objects.create()
        else:
            cart = session_cart

    request.session["cart_id"] = cart.pk
    return cart


def add_to_cart(request: HttpRequest, slug: str) -> HttpResponse:
    """Add the selected product to the active cart and redirect back."""

    product = get_object_or_404(Product, slug=slug)
    next_url = request.GET.get("next")
    next_url_is_safe = bool(
        next_url
        and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )
    )

    if product.stock <= 0:
        if next_url_is_safe:
            return redirect(next_url)
        return redirect(product.get_absolute_url())

    cart = _get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if cart_item.quantity > product.stock:
        cart_item.quantity = product.stock
        cart_item.save(update_fields=["quantity"])
    elif not created:
        if cart_item.quantity + 1 > product.stock:
            # Quantity already at stock level; do not increase beyond available stock.
            pass
        else:
            cart_item.quantity += 1
            cart_item.save(update_fields=["quantity"])

    if next_url_is_safe:
        return redirect(next_url)
    return redirect(reverse("cart:home"))
