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

