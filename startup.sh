# path to this file: "dml-marketing-middleware/>file<"
#!/usr/bin/env bash
set -euo pipefail

echo "Starting…"

# Always run from the deployed app folder (this is where manage.py is)
if [ -f /home/site/app/manage.py ]; then
  cd /home/site/app
else
  echo "ERROR: /home/site/app/manage.py not found"
  ls -la /home/site || true
  exit 1
fi

echo "Running in: $(pwd)"
echo "SQLITE_PATH=${SQLITE_PATH:-}"
python -V

# Ensure DB folder exists (it will, but safe)
mkdir -p /home/site

# Run migrations against the configured DB
python manage.py migrate --noinput

# Optional sanity print
python manage.py shell -c "from django.conf import settings; print('DB:', settings.DATABASES['default']['NAME'])"

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --error-logfile -