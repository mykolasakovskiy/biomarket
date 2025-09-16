from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import UserProfile


def profile_overview(request: HttpRequest) -> HttpResponse:
    """Display a minimal placeholder profile page for the current user."""
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        message = f"Profile for {profile.user.get_username()}"
    else:
        message = "Anonymous profile placeholder"
    return HttpResponse(message, content_type="text/plain")


def profile_detail(request: HttpRequest, username: str) -> HttpResponse:
    user_model = get_user_model()
    user = get_object_or_404(user_model, username=username)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return HttpResponse(f"Profile page for {profile.user.get_username()}", content_type="text/plain")
