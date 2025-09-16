from decimal import Decimal

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from products.models import Product

from .models import Cart, CartItem


STOCK_LIMIT_MESSAGE = (
    "На жаль, товару більше немає на складі. Додано максимально доступну кількість."
)


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
            for item in session_cart.items.select_related("product"):
                destination_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=item.product,
                    defaults={"quantity": item.quantity},
                )

                product_stock = destination_item.product.stock

                if created:
                    capped_quantity = min(destination_item.quantity, product_stock)
                    if capped_quantity != destination_item.quantity:
                        destination_item.quantity = capped_quantity
                        destination_item.save(update_fields=["quantity"])
                        messages.info(request, STOCK_LIMIT_MESSAGE)
                else:
                    desired_quantity = destination_item.quantity + item.quantity
                    capped_quantity = min(desired_quantity, product_stock)

                    if capped_quantity != destination_item.quantity:
                        destination_item.quantity = capped_quantity
                        destination_item.save(update_fields=["quantity"])

                    if capped_quantity < desired_quantity:
                        messages.info(request, STOCK_LIMIT_MESSAGE)

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

    if product.stock <= 0:
        return redirect(request.GET.get("next") or product.get_absolute_url())

    cart = _get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        desired_quantity = cart_item.quantity + 1
        capped_quantity = min(desired_quantity, product.stock)

        if capped_quantity != cart_item.quantity:
            cart_item.quantity = capped_quantity
            cart_item.save(update_fields=["quantity"])

        if capped_quantity < desired_quantity:
            messages.info(request, STOCK_LIMIT_MESSAGE)

    redirect_url = request.GET.get("next") or reverse("cart:home")
    return redirect(redirect_url)
