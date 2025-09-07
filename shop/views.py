from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Product, Category, Order, OrderItem
from .forms import CheckoutForm
from .utils import add_to_cart, remove_from_cart, get_cart, clear_cart

class ProductListView(ListView):
    model = Product
    paginate_by = 12
    template_name = "shop/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("category")
        slug = self.kwargs.get("slug")
        if slug:
            qs = qs.filter(category__slug=slug)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(title__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["active_category"] = self.kwargs.get("slug")
        return ctx

class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

def cart_view(request):
    cart = get_cart(request)
    items = []
    total = Decimal("0.00")
    ids = [int(pid) for pid in cart.keys()]
    products = {p.id: p for p in Product.objects.filter(id__in=ids)}
    for pid, item in cart.items():
        p = products.get(int(pid))
        if not p:
            continue
        line_total = Decimal(item['price']) * item['qty']
        total += line_total
        items.append({"product": p, "qty": item['qty'], "line_total": line_total})
    return render(request, "shop/cart.html", {"items": items, "total": total})

def cart_add(request, product_id):
    qty = int(request.GET.get("qty", "1"))
    add_to_cart(request, product_id, qty)
    return redirect("shop:cart")

def cart_remove(request, product_id):
    remove_from_cart(request, product_id)
    return redirect("shop:cart")

def checkout(request):
    cart = get_cart(request)
    if not cart:
        return redirect("shop:home")
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Calculate total
            from decimal import Decimal
            total = sum(Decimal(item['price']) * item['qty'] for item in cart.values())
            order = Order.objects.create(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
                notes=form.cleaned_data.get('notes', ''),
                total=total,
            )
            # Create items
            ids = [int(pid) for pid in cart.keys()]
            products = {p.id: p for p in Product.objects.filter(id__in=ids)}
            for pid, item in cart.items():
                p = products.get(int(pid))
                if not p:
                    continue
                OrderItem.objects.create(order=order, product=p, price=item['price'], quantity=item['qty'])

            request.session['current_order_id'] = order.id
            # Redirect to payment (Stripe example) or show bank details/COD
            return redirect("shop:stripe_create_checkout")
    else:
        form = CheckoutForm()
    return render(request, "shop/checkout.html", {"form": form})

def order_success(request):
    order_id = request.GET.get("order_id")
    return render(request, "shop/order_success.html", {"order_id": order_id})

# ---- Stripe payment (example stub) ----
def stripe_create_checkout(request):
    import stripe
    order_id = request.session.get('current_order_id')
    if not order_id:
        return redirect("shop:home")
    order = Order.objects.get(id=order_id)

    stripe.api_key = settings.STRIPE_SECRET_KEY or ""
    if not stripe.api_key:
        # Dev fallback: mark as paid and show success (no real payment)
        order.paid = True
        order.payment_provider = "dev"
        order.payment_id = "TEST-NO-STRIPE"
        order.save()
        clear_cart(request)
        return redirect(reverse("shop:order_success") + f"?order_id={order.id}")

    # Create a real Stripe Checkout session
    line_items = []
    for item in order.items.all():
        line_items.append({
            "price_data": {
                "currency": (getattr(settings, 'CURRENCY', 'UAH')).lower(),
                "product_data": {"name": item.product.title},
                "unit_amount": int(Decimal(item.price) * 100),
            },
            "quantity": item.quantity,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
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

@csrf_exempt
def stripe_webhook(request):
    # Minimal stub – implement signature verification with STRIPE_WEBHOOK_SECRET
    return HttpResponse(status=200)
