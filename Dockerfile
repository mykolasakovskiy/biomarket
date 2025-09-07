# Dockerfile (Render-friendly)

FROM python:3.12-slim

# Python env
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# System deps (для psycopg2 та компіляції C-розширень)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# App
COPY . .

# Збирання статичних файлів (не впаде, якщо DEBUG=1)
RUN mkdir -p /app/staticfiles && python manage.py collectstatic --noinput || true

# (не обовʼязково для Render, але не шкодить)
EXPOSE 8000

# 1) Міграції на старті
# 2) Запуск gunicorn. Якщо Render не передасть PORT, візьмемо 8000.
CMD ["sh","-c","python manage.py makemigrations --noinput && python manage.py migrate --noinput && gunicorn biomarket.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]

