#!/bin/sh
set -e

# Міграції БД
python manage.py migrate --noinput

# Статика (без падіння, якщо нічого збирати)
python manage.py collectstatic --noinput || true

# Наповнення демо-даними (ідемпотентно — дублікати не створює)
python manage.py seed_biomarket || true

# Запуск сервера
gunicorn biomarket.wsgi:application --bind 0.0.0.0:8000 --preload
