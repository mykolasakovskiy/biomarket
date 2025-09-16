from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.utils.text import Truncator

from .models import Product


def product_list(request):
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "").strip()

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    valid_sorts = {"price": "price", "name": "name"}
    if sort in valid_sorts:
        products = products.order_by(valid_sorts[sort])

    description = (
        "Каталог Biomarket: натуральні та органічні товари для здорового життя, "
        "доступні за вигідними цінами."
    )
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    meta_title = "Каталог товарів Biomarket"
    if page_obj.number > 1:
        meta_title = f"Каталог товарів Biomarket – сторінка {page_obj.number}"

    query_params = request.GET.copy()
    if "page" in query_params:
        query_params.pop("page")
    preserved_query = query_params.urlencode()

    context = {
        "products": page_obj.object_list,
        "q": query,
        "current_sort": sort if sort in {"price", "name"} else "",
        "meta_title": meta_title,
        "description": description,
        "keywords": "Biomarket, каталог товарів, органічні продукти, еко продукти",
        "og_type": "website",
        "twitter_card": "summary",
        "page_obj": page_obj,
        "preserved_query": preserved_query,
    }
    return render(request, "products/list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    description_source = product.description or f"Купити {product.name} в Biomarket"
    description = Truncator(description_source).chars(160)
    meta_image = None
    if product.image:
        meta_image = request.build_absolute_uri(product.image.url)
    context = {
        "product": product,
        "meta_title": f"{product.name} — Biomarket",
        "description": description,
        "keywords": f"{product.name}, Biomarket, органічні товари",
        "og_type": "product",
        "meta_image": meta_image,
        "twitter_card": "summary_large_image" if meta_image else "summary",
    }
    return render(request, "products/detail.html", context)
