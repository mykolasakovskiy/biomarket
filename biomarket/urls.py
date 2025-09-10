# biomarket/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.conf.urls.static import static
from django.core.management import call_command

def seed_demo(request):
    # простий захист токеном: ?token=YOUR_TOKEN
    token = request.GET.get("token")
    expected = getattr(settings, "SEED_TOKEN", None)
    if expected and token != expected:
        return HttpResponseForbidden("Forbidden")

    # 1) спробувати завантажити фікстуру, якщо є
    try:
        call_command("loaddata", "biomarket/fixtures/sample_products.json", verbosity=0)
        return HttpResponse("✅ Loaded fixture sample_products.json")
    except Exception:
        # 2) fallback: створити кілька демо-товарів у коді
        try:
            from shop.models import Product, Category
            from django.utils.text import slugify

            fruits, _ = Category.objects.get_or_create(name="Фрукти", defaults={"slug": "frukty"})
            vegs, _   = Category.objects.get_or_create(name="Овочі", defaults={"slug": "ovochi"})

            demo = [
                ("Яблука органічні", "Свіжі, хрумкі, солодкі.", 55.00, fruits),
                ("Груші фермерські", "Ароматні й соковиті.", 68.00, fruits),
                ("Морква", "Солодка молода морква.", 29.00, vegs),
                ("Буряк столовий", "Ідеальний для борщу.", 24.00, vegs),
                ("Картопля молода", "Молода, тонка шкірка.", 22.00, vegs),
                ("Цибуля ріпчаста", "Універсальна в кулінарії.", 19.00, vegs),
            ]

            created = 0
            for name, desc, price, cat in demo:
                slug = slugify(name)
                obj, was_created = Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "description": desc,
                        "price": price,
                        "category": cat,
                        "available": True,
                    },
                )
                if was_created:
                    created += 1

            return HttpResponse(f"✅ Seeded {created} demo products (fallback)")
        except Exception as ee:
            return HttpResponse(f"⚠️ Seed failed: {ee}")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("shop.urls", "shop"), namespace="shop")),
    path("seed/", seed_demo),  # одноразовий ендпойнт
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
