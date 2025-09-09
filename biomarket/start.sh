#!/usr/bin/env bash
set -e

python manage.py migrate --noinput
# Collect static again at runtime just in case
python manage.py collectstatic --noinput || true

echo "Starting Gunicorn..."
exec gunicorn biomarket.wsgi:application --bind 0.0.0.0:${PORT:-8000} --preload
