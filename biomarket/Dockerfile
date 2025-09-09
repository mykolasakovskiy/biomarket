FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=biomarket.settings \
    PORT=8000

# Collect static at build (safe even if nothing)
RUN python manage.py collectstatic --noinput || true

# Start script runs migrations then gunicorn
RUN chmod +x start.sh
CMD ["./start.sh"]
