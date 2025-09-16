from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class ProfileDetailViewTests(TestCase):
    def test_profile_detail_does_not_create_profile(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="example-password",
        )

        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        initial_profile_count = UserProfile.objects.count()

        response = self.client.get(reverse("accounts:detail", args=[user.username]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserProfile.objects.count(), initial_profile_count)

    def test_profile_detail_old_path_redirects(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="carol",
            email="carol@example.com",
            password="example-password",
        )

        response = self.client.get(f"/accounts/{user.username}/")

        self.assertRedirects(
            response,
            reverse("accounts:detail", args=[user.username]),
            status_code=301,
            target_status_code=200,
        )


class ProfileOverviewViewTests(TestCase):
    def test_profile_overview_creates_missing_profile(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="example-password",
        )

        UserProfile.objects.filter(user=user).delete()
        self.assertFalse(UserProfile.objects.filter(user=user).exists())

        self.client.force_login(user)
        response = self.client.get(reverse("accounts:overview"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
