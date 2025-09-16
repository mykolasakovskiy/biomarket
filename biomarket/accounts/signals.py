"""Signal handlers for the accounts application."""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Ensure each user has an associated profile."""

    if not created:
        return

    UserProfile.objects.get_or_create(user=instance)
