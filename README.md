# Biomarket

Biomarket — мінімальний стартовий проєкт на Django для демонстрації базового каталогу товарів.

## Швидкий старт

1. Створіть віртуальне середовище та активуйте його:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. Встановіть залежності та підготуйте базу даних:

```bash
cd biomarket
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```

3. Перед запуском налаштуйте змінні середовища (наприклад, у файлі `.env` в корені проєкту):

```
DJANGO_SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
DEBUG=1
```

`DJANGO_SECRET_KEY` та `ALLOWED_HOSTS` обов'язково повинні бути визначені у робочому середовищі (напр., через Render, Docker або хмарну платформу).

4. Запустіть сервер розробника:

```bash
python manage.py runserver
```

Після запуску відкрийте [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Структура проєкту

- `manage.py` — точка входу для команд Django.
- `biomarket/` — налаштування та модулі застосунку.
- `templates/` — HTML-шаблони.
- `static/` та `staticfiles/` — статичні файли.

