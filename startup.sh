#!/usr/bin/env bash
set -euo pipefail

cd /home/site/app

echo "== Startup running =="
echo "PWD: $(pwd)"
ls -la | head -80

# Activate the venv that actually has Django installed
source /home/site/app/antenv/bin/activate

echo "== Python =="
which python
python -V

echo "== Django check =="
python -c "import django; print('Django OK:', django.get_version())"

echo "== Migrations =="
python manage.py migrate --noinput

echo "== Start gunicorn =="
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --error-logfile -
