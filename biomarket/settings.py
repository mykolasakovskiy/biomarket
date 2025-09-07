# biomarket/settings.py
from pathlib import Path
import os
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────────────────────
# БАЗОВЕ
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
# Для локалки читаємо .env (на Render .env зазвичай немає — значення беруться з UI)
load_dotenv(BASE_DIR / ".env")

# Безпечний парсинг DEBUG: "1/true/yes" => True
DEBUG = os.getenv("DEBUG", "0").lower() in ("1", "true", "yes")

# SECRET_KEY: обов'язково задайте в продакшені через змінні оточення
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key-change-me")

# ALLOWED_HOSTS: з env через кому; обрізаємо пробіли й ігноруємо порожні
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

# Якщо Render задає ім'я хоста окремо — додамо (не обов'язково, але зручно)
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# ──────────────────────────────────────────────────────────────────────────────
# ДОДАТКИ
# ──────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "shop",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise — віддавання статичних файлів у продакшені
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "biomarket.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "shop.context_processors.cart",
            ],
        },
    },
]

WSGI_APPLICATION = "biomarket.wsgi.application"

# ──────────────────────────────────────────────────────────────────────────────
# БАЗА ДАНИХ
# SQLite для розробки; Postgres вмикаємо через USE_POSTGRES=1
# ──────────────────────────────────────────────────────────────────────────────
if os.getenv("USE_POSTGRES", "0") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "biomarket"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": 60,  # тримати конекшени відкритими
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ──────────────────────────────────────────────────────────────────────────────
# МОВА / ЧАС
# ──────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "uk"
TIME_ZONE = os.getenv("TZ", "Europe/Kyiv")
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────────────────────────────────────
# СТАТИЧНІ ТА МЕДІА
# ──────────────────────────────────────────────────────────────────────────────
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # для розробки (якщо є папка static/)
STATIC_ROOT = BASE_DIR / "staticfiles"    # куди collectstatic складає файли на проді
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ──────────────────────────────────────────────────────────────────────────────
# БЕЗПЕКА / PROXY
# ──────────────────────────────────────────────────────────────────────────────
# Дозволяє Django коректно визначати HTTPS за проксі (Render)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Куки лише по https у продакшені
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = not DEBUG

# CSRF Trusted Origins з env (через кому, повні схеми: https://…)
CSRF_TRUSTED_ORIGINS = [
    u.strip() for u in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if u.strip()
]
if RENDER_EXTERNAL_HOSTNAME:
    origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

# ──────────────────────────────────────────────────────────────────────────────
# ПЛАТЕЖІ / КОШИК / ВАЛЮТА
# ──────────────────────────────────────────────────────────────────────────────
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

CART_SESSION_ID = "cart"
CURRENCY = os.getenv("CURRENCY", "UAH")

# ──────────────────────────────────────────────────────────────────────────────
# ЛОГУВАННЯ (щоб 500 помилки було видно в Render Logs)
# ──────────────────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
    },
}
