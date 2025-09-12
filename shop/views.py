from decimal import Decimal
from django.conf import settings
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView

try:
    import stripe
except Exception:
    stripe = None

from .models import Product, Category, Order, OrderItem
from .forms import CheckoutForm
from .utils import add_to_cart, remove_from_cart, get_cart, clear_cart


class ProductListView(ListView):
    model = Product
    context_object_name = "products"
    paginate_by = 12
    template_name = "shop/product_list.html"

    def get_queryset(self):
        qs = (
            Product.objects.filter(available=True)
            .select_related("category")
        )

        # Категорія з URL kwargs (/category/<slug>/) або з ?category=<slug>
        slug = self.kwargs.get("slug") or self.request.GET.get("category")
        if slug:
            qs = qs.filter(category__slug=slug)

        # Пошук за назвою та описом: ?q=...
        q = self.request.GET.get("q")
        if q:
            q = q.strip()
            if q:
                                qs = qs.filter(Q(title__icontains=q))

        return qs.order_by("title")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Категорії з лічильником товарів
        ctx["categories"] = Category.objects.annotate(count=Count("product")).order_by("name")
        ctx["current_category_slug"] = self.kwargs.get("slug") or self.request.GET.get("category")
        ctx["search_query"] = self.request.GET.get("q", "")
        ctx["currency"] = getattr(settings, "CURRENCY", "UAH")
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["currency"] = getattr(settings, "CURRENCY", "UAH")
        return ctx


def cart_view(request):
    cart = get_cart(request)
    items = []
    total = Decimal("0.00")

    for pid, item in cart.items():
        price = Decimal(item["price"])
        qty = int(item["qty"])
        subtotal = price * qty
        items.append(
            {
                "id": int(pid),
                "name": item.get("title") or item.get("name"),  # підтримка обох ключів
                "price": price,
                "qty": qty,
                "slug": item.get("slug"),
                "subtotal": subtotal,
            }
        )
        total += subtotal

    return render(
        request,
        "shop/cart.html",
        {"items": items, "total": total, "currency": getattr(settings, "CURRENCY", "UAH")},
    )


def cart_add(request, product_id):
    qty = int(request.GET.get("qty", 1))
    add_to_cart(request, product_id, qty)
    return redirect("shop:cart")


def cart_remove(request, product_id):
    remove_from_cart(request, product_id)
    return redirect("shop:cart")


def checkout(request):
    cart = get_cart(request)
    if not cart:
        # Якщо кошик порожній — назад до списку товарів
        return redirect("shop:product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Створення замовлення
            order = Order.objects.create(
                full_name=form.cleaned_data["full_name"],
                email=form.cleaned_data["email"],
                phone=form.cleaned_data["phone"],
                address=form.cleaned_data["address"],
                city=form.cleaned_data["city"],
                postal_code=form.cleaned_data["postal_code"],
                notes=form.cleaned_data.get("notes", ""),
            )

            total = Decimal("0.00")
            for pid, item in cart.items():
                price = Decimal(item["price"])
                qty = int(item["qty"])
                product = get_object_or_404(Product, id=int(pid))
                OrderItem.objects.create(order=order, product=product, price=price, quantity=qty)
                total += price * qty

            order.total = total

            # Stripe інтеграція (за наявності ключів)
            stripe_pk = getattr(settings, "STRIPE_PUBLIC_KEY", None)
            stripe_sk = getattr(settings, "STRIPE_SECRET_KEY", None)

            if stripe_sk and stripe:
                stripe.api_key = stripe_sk
                currency = getattr(settings, "STRIPE_CURRENCY", "uah")

                line_items = []
                for it in order.items.all():
                    # Використовуємо назву товару з моделі Product.name
                    line_items.append(
                        {
                            "price_data": {
                                "currency": currency,
                                "product_data": {"name": it.product.name},
                                "unit_amount": int(it.price * 100),  # копійки
                            },
                            "quantity": it.quantity,
                        }
                    )

                session = stripe.checkout.Session.create(
                    mode="payment",
                    line_items=line_items,
                    success_url=request.build_absolute_uri(reverse("shop:order_success")) + f"?order_id={order.id}",
                    cancel_url=request.build_absolute_uri(reverse("shop:cart")),
                    metadata={"order_id": str(order.id)},
                )

                order.payment_provider = "stripe"
                order.payment_id = session.id
                order.save()

                clear_cart(request)
                return redirect(session.url, code=303)

            # Fallback без Stripe: позначаємо як оплачене (для розробки/тесту)
            order.payment_provider = "dummy"
            order.payment_id = "test"
            order.paid = True
            order.save()
            clear_cart(request)
            return redirect(reverse("shop:order_success") + f"?order_id={order.id}")

    else:
        form = CheckoutForm()

    # Підсумки для сторінки підтвердження
    items = []
    total = Decimal("0.00")
    for pid, item in cart.items():
        price = Decimal(item["price"])
        qty = int(item["qty"])
        subtotal = price * qty
        items.append(
            {
                "id": int(pid),
                "name": item.get("title") or item.get("name"),
                "price": price,
                "qty": qty,
                "slug": item.get("slug"),
                "subtotal": subtotal,
            }
        )
        total += subtotal

    return render(request, "shop/checkout.html", {"form": form, "items": items, "total": total})


def order_success(request):
    order_id = request.GET.get("order_id")
    return render(request, "shop/order_success.html", {"order_id": order_id})


def stripe_create_checkout(request):
    return HttpResponseBadRequest("Use POST /checkout to create an order first.")


@csrf_exempt
def stripe_webhook(request):
    # TODO: Реалізуйте перевірку підпису з STRIPE_WEBHOOK_SECRET при потребі
    return HttpResponse(status=200)

