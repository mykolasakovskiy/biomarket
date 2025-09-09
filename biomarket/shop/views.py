from django.views.generic import ListView
from .models import Product

class ProductListView(ListView):
    model = Product
    template_name = "shop/product_list.html"
    context_object_name = "products"
