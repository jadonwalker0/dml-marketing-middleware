#!/usr/bin/env bash
set -euo pipefail

echo "== Startup running =="
echo "PWD: $(pwd)"
ls -la | head -80

echo "== Python being used =="
which python || true
python -V || true

echo "== Install deps if needed (safe no-op if already installed) =="
pip -V || true

echo "== Migrations =="
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput

echo "== Quick sanity checks =="
python - <<'PY'
from django.conf import settings
print("DB PATH:", settings.DATABASES["default"]["NAME"])
PY

echo "== Start gunicorn =="
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --error-logfile -
