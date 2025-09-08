from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Підключаємо shop з namespace='shop'
    path("", include(("shop.urls", "shop"), namespace="shop")),
]

# У продакшені статику віддає WhiteNoise; тут додаємо лише медіа під час DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
