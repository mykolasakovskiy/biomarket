from decimal import Decimal
from django.conf import settings
from .utils import get_cart

def cart(request):
    cart = get_cart(request)
    total = sum(Decimal(item['price']) * item['qty'] for item in cart.values())
    return {
        'cart_total_items': sum(item['qty'] for item in cart.values()),
        'cart_total_sum': total,
        'currency': getattr(settings, 'CURRENCY', 'UAH')
    }
