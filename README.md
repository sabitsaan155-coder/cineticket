# GearLoop

GearLoop is a training platform for renting and booking sports and outdoor equipment. The project is built as a full Django service with public UI, user accounts, admin, and API.

## Stack
- Django
- PostgreSQL (prod) / SQLite (local)
- gunicorn + nginx
- WhiteNoise (static)

## Status
- Project skeleton, base pages, and apps structure are ready.
- Next: MVP and full requirements.

## Apps
- core
- accounts
- catalog
- rentals
- orders
- reviews
- favorites
- pages
- search
- api
- dashboard

## Quick start (local, SQLite)
1. Create venv and install dependencies:
   - `python -m venv .venv`
   - `./.venv/Scripts/python -m pip install -r requirements.txt`
2. Set environment variables:
   - `copy .env.example .env`
   - Set `SECRET_KEY` and keep `DEBUG=1`
3. Migrations and run:
   - `./.venv/Scripts/python manage.py migrate`
   - `./.venv/Scripts/python manage.py createsuperuser`
   - `./.venv/Scripts/python manage.py runserver`

## Production run (PostgreSQL)
1. Environment variables (example):
   - `DEBUG=0`
   - `SECRET_KEY=...`
   - `ALLOWED_HOSTS=gearloop.example.com`
   - `CSRF_TRUSTED_ORIGINS=https://gearloop.example.com`
   - `DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/gearloop`
   - `SECURE_SSL_REDIRECT=1`
   - `SESSION_COOKIE_SECURE=1`
   - `CSRF_COOKIE_SECURE=1`
   - `SECURE_HSTS_SECONDS=31536000`
2. Migrations and static:
   - `./.venv/Scripts/python manage.py migrate`
   - `./.venv/Scripts/python manage.py collectstatic`
3. Run gunicorn:
   - `./.venv/Scripts/gunicorn config.wsgi:application --bind 0.0.0.0:8000`
4. Nginx:
   - Proxy to gunicorn, serve `staticfiles/` and `media/`.

## Static and media
- `STATIC_ROOT` is used by `collectstatic`.
- `MEDIA_ROOT` stores uploads.
- In production, configure nginx to serve `staticfiles/` and `media/`.

## Logs and restart
- Django logs are written to `logs/django.log`.
- Restart: `systemctl restart gunicorn` (or your process manager).

## Backup strategy
- Regular PostgreSQL dumps (daily + weekly snapshots).
- Store backups in separate storage (S3/cloud/FTP).

## API
Will include 5+ endpoints with filters, unified error format, and protected POST/PUT/DELETE.

## Template
UI will be based on a free HTML/CSS template from the internet and integrated into `templates/` and `static/`.

## Acceptance checklist
- [ ] 10+ apps
- [ ] 15+ UI pages
- [ ] 15 CSS effects
- [ ] 15 JS scenarios
- [ ] Models and relations, slug URLs
- [ ] Admin and permissions
- [ ] API 5+ endpoints
- [ ] Seed/fixtures
- [ ] Prod settings: DEBUG=False, ALLOWED_HOSTS, HTTPS, collectstatic
- [ ] Deployment checklist and instructions
