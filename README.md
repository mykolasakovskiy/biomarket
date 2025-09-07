# BioMarket (Django) — Стартер для магазину біо продукції

Швидкий старт готового інтернет‑магазину на Django 5:
- Каталог (категорії, товари, зображення URL)
- Кошик у сесії
- Оформлення замовлення (Order + OrderItem)
- Оплата через Stripe (стаб), або миттєвий success у дев‑режимі
- Українська локаль, часовий пояс `Europe/Kyiv`
- Bootstrap 5 інтерфейс

## Як запустити локально
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Налаштуйте змінні в .env за потреби
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Відкрийте http://127.0.0.1:8000/ — додайте категорії/товари через /admin/.

## Оплата
У `.env` заповніть ключі STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY та STRIPE_WEBHOOK_SECRET.
Якщо ключів нема — після натискання «Перейти до оплати» замовлення автоматично позначається оплаченим (для тестування).

## Продакшн
- Використати Postgres (встановити `USE_POSTGRES=1` і змінні POSTGRES_*).
- Налаштувати `ALLOWED_HOSTS`, HTTPS, статичні файли (whitenoise або CDN), бекапи БД.
- Додати зберігання зображень (S3/Cloudinary) замість `image_url`.
- Замінити Stripe або додати локальних провайдерів (LiqPay/Fondy/WayForPay).
- Додати доставку (Нова Пошта API), SEO сторінки, купони, блог, e‑mail нотифікації.

## Структура
```
biomarket/        # проект
shop/             # додаток (каталог, кошик, замовлення, Stripe-stub)
templates/
static/
.env
requirements.txt
```

Успіхів! 🌿
