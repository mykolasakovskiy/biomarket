from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.profile_overview, name="overview"),
    path("<str:username>/", views.profile_detail, name="detail"),
]
