FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Collect static on build (optional); won't fail if DEBUG=1
RUN python manage.py collectstatic --noinput || true

CMD ["sh", "-c", "gunicorn biomarket.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]

