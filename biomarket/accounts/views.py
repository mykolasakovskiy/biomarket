from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model

from .models import UserProfile


def profile_overview(request: HttpRequest) -> HttpResponse:
    """Display a profile overview page for the current user."""

    profile = None
    meta_title = "Профіль гостя — Biomarket"
    description = "Увійдіть до Biomarket, щоб переглянути персональний профіль та історію замовлень."
    keywords = "Biomarket, профіль, обліковий запис"

    if request.user.is_authenticated:
        profile, _created = UserProfile.objects.get_or_create(user=request.user)

        username = profile.user.get_username()
        meta_title = f"Профіль {username} — Biomarket"
        description = f"Персональна інформація та контактні дані користувача {username} в Biomarket."
        keywords = f"Biomarket, профіль користувача, {username}"

    context = {
        "profile": profile,
        "meta_title": meta_title,
        "description": description,
        "keywords": keywords,
        "og_type": "profile",
        "twitter_card": "summary",
    }

    return render(request, "accounts/overview.html", context)


def profile_detail(request: HttpRequest, username: str) -> HttpResponse:
    """Display a detailed public profile page for the selected user."""

    user_model = get_user_model()
    user = get_object_or_404(user_model, username=username)
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist as exc:
        raise Http404("Profile not found") from exc
    is_owner = request.user.is_authenticated and request.user.pk == user.pk

    context = {
        "profile": profile,
        "profile_user": user,
        "is_owner": is_owner,
        "meta_title": f"Профіль {user.get_username()} — Biomarket",
        "description": f"Публічний профіль користувача {user.get_username()} на Biomarket.",
        "keywords": f"Biomarket, профіль користувача, {user.get_username()}",
        "og_type": "profile",
        "twitter_card": "summary",
    }

    return render(request, "accounts/detail.html", context)
