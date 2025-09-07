from decimal import Decimal
from django.conf import settings
from .models import Product

def get_cart(request):
    return request.session.get(settings.CART_SESSION_ID, {})

def save_cart(request, cart):
    request.session[settings.CART_SESSION_ID] = cart
    request.session.modified = True

def add_to_cart(request, product_id, qty=1):
    cart = get_cart(request)
    product = Product.objects.get(id=product_id)
    pid = str(product_id)
    if pid not in cart:
        cart[pid] = {'title': product.title, 'price': str(product.price), 'qty': 0, 'slug': product.slug}
    cart[pid]['qty'] += int(qty)
    save_cart(request, cart)

def remove_from_cart(request, product_id):
    cart = get_cart(request)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        save_cart(request, cart)

def clear_cart(request):
    save_cart(request, {})
