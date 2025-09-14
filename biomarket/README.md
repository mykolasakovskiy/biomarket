# Biomarket (Django)

Мінімальний стартовий проєкт.

## Швидкий старт
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

cd biomarket
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

Відкрий http://127.0.0.1:8000
