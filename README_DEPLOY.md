# Biomarket — Deploy Template (Django + Render)

This repo is configured for Render/Heroku-like deployment.

## What’s included
- `requirements.txt` with `dj-database-url`, `whitenoise`, `gunicorn`, etc.
- `render.yaml` with `preDeployCommand: python manage.py migrate`
- `Procfile` for gunicorn
- `Dockerfile` (optional path)
- `biomarket/settings.py` configured to:
  - read `DATABASE_URL` (Postgres) or fallback to SQLite
  - serve static via WhiteNoise
  - use `STATICFILES_DIRS = [BASE_DIR / "static"]`
  - trust Render hostname for CSRF

## Quick start (local)
```bash
python -m venv .venv
source .venv/bin/activate  # .venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Deploy on Render
1. Create a new **Web Service** from this repo.
2. Add **PostgreSQL** instance and set `DATABASE_URL` in your service **Environment**.
3. Set `DJANGO_SETTINGS_MODULE=biomarket.settings`.
4. Optional: set `ALLOWED_HOSTS=.onrender.com,yourdomain.com`.
5. Deploy — `render.yaml` will run migrations automatically.

## Notes
- Commit your app migrations from `shop/migrations/` so the deploy can run them.
- Put your project static files in `static/` (e.g., `static/shop/...`).
