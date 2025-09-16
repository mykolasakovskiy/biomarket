from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Accounts"

    def ready(self) -> None:  # pragma: no cover - Django hook
        """Load signal handlers when the app is ready."""

        # Importing signals ensures they are registered once Django starts.
        import accounts.signals  # noqa: F401

        super().ready()
