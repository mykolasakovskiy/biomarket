from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.profile_overview, name="overview"),
    path("user/<str:username>/", views.profile_detail, name="detail"),
    path(
        "<str:username>/",
        RedirectView.as_view(pattern_name="accounts:detail", permanent=True),
        name="legacy_detail",
    ),
]
