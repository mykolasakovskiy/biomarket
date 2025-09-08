FROM python:3.12-slim

# Базові налаштування Python
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# Встановлення залежностей
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Код
COPY . .

# Django settings
ENV DJANGO_SETTINGS_MODULE=biomarket.settings

# Збирання статики (не впаде, якщо її мало)
RUN python manage.py collectstatic --noinput || true

# Міграції та автосід (тільки якщо БД порожня), потім gunicorn на $PORT
CMD sh -c "python manage.py migrate --noinput && python manage.py seed_shop --if-empty && gunicorn biomarket.wsgi:application --bind 0.0.0.0:${PORT:-8000} --preload"
