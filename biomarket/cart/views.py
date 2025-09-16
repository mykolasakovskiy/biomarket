from django.http import HttpRequest, HttpResponse


def cart_home(request: HttpRequest) -> HttpResponse:
    """Display a minimal placeholder cart page."""
    return HttpResponse("Cart is empty", content_type="text/plain")
