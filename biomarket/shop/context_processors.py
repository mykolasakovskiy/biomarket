from decimal import Decimal
from .utils import get_cart
from .models import Category

def cart(request):
    cart = get_cart(request)
    total = Decimal("0.00")
    items_count = 0
    for _, item in cart.items():
        total += Decimal(item.get("price", 0)) * int(item.get("qty", 0))
        items_count += int(item.get("qty", 0))
    return {
        "cart_total_items": items_count,
        "cart_total_sum": total,
    }

def categories(request):
    try:
        cats = Category.objects.all().order_by("name")
    except Exception:
        cats = []
    return {"categories_menu": cats}
