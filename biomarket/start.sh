#!/usr/bin/env bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

# === Auto-create superuser from env (idempotent) ===
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
python - <<'PY'
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","biomarket.settings")
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
u = os.environ["DJANGO_SUPERUSER_USERNAME"]
e = os.environ["DJANGO_SUPERUSER_EMAIL"]
p = os.environ["DJANGO_SUPERUSER_PASSWORD"]
if not User.objects.filter(username=u).exists():
    User.objects.create_superuser(u, e, p)
    print("✅ Superuser created.")
else:
    print("ℹ️ Superuser exists, skipping.")
PY
fi

echo "Starting Gunicorn..."
exec gunicorn biomarket.wsgi:application --bind 0.0.0.0:${PORT:-8000} --preload
