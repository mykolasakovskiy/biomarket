# Biomarket

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
cd biomarket
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

Open http://127.0.0.1:8000

## Environment variables

- `DJANGO_DEBUG` – set to `True` to enable Django debug mode (default: `False`).
- `DJANGO_ALLOWED_HOSTS` – comma-separated list of allowed host names (default: `*`).

