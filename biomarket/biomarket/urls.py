from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import TemplateView

from .sitemaps import ProductSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
}

urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="index.html",
            extra_context={
                "meta_title": "Biomarket — органічні продукти та еко товари",
                "description": "Biomarket пропонує широкий вибір органічних та еко товарів для здорового життя.",
                "keywords": "Biomarket, органічні продукти, еко товари, здорова їжа",
                "og_type": "website",
                "twitter_card": "summary",
            },
        ),
        name="home",
    ),
    path(
        "about/",
        TemplateView.as_view(
            template_name="about.html",
            extra_context={
                "meta_title": "Про Biomarket",
                "description": "Дізнайтеся більше про місію Biomarket та наш підхід до відбору еко-продуктів.",
                "keywords": "Biomarket, про компанію, місія, еко продукти",
                "og_type": "website",
                "twitter_card": "summary",
            },
        ),
        name="about",
    ),
    path(
        "contacts/",
        TemplateView.as_view(
            template_name="contact.html",
            extra_context={
                "meta_title": "Контакти Biomarket",
                "description": "Зв'яжіться з Biomarket: телефони, email та адреса для замовлень органічних продуктів.",
                "keywords": "Biomarket контакти, служба підтримки, органічні продукти",
                "og_type": "website",
                "twitter_card": "summary",
            },
        ),
        name="contacts",
    ),
    path("products/", include("products.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]
