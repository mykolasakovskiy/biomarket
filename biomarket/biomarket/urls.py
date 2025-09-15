from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),
    path("contacts/", TemplateView.as_view(template_name="contact.html"), name="contacts"),
    path("products/", include("products.urls")),
]
