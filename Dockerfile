FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=biomarket.settings

# Collect static files (safe if none yet)
RUN python manage.py collectstatic --noinput || true

CMD ["gunicorn", "biomarket.wsgi:application", "--bind", "0.0.0.0:8000", "--preload"]
