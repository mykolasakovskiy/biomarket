FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Системні залежності (за потреби можна додати build-essential, libpq-dev тощо)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Python-залежності
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Код
COPY . .

# Django settings (якщо не задаєш у Envs Render)
ENV DJANGO_SETTINGS_MODULE=biomarket.settings

# Вписуємо entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# (Опційно) збір статики вже під час build — не обов’язково
# RUN python manage.py collectstatic --noinput || true

# Старт
CMD ["/entrypoint.sh"]

