#!/usr/bin/env bash
set -euo pipefail

echo "Starting…"

# Always run from the deployed app folder (this is where manage.py is)
APP_DIR="/home/site/app"
if [ -f "${APP_DIR}/manage.py" ]; then
  cd "${APP_DIR}"
else
  echo "ERROR: ${APP_DIR}/manage.py not found"
  echo "Contents of /home/site:"
  ls -la /home/site || true
  echo "Contents of /home/site/wwwroot:"
  ls -la /home/site/wwwroot || true
  exit 1
fi

echo "Running in: $(pwd)"
python -V

# Show key env (safe ones)
echo "DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-<not set>}"
echo "DB_HOST=${DB_HOST:-<not set>}"
echo "DB_NAME=${DB_NAME:-<not set>}"
echo "DB_USER=${DB_USER:-<not set>}"
echo "DB_PORT=${DB_PORT:-<not set>}"

# Run migrations
echo "Running migrations…"
python manage.py migrate --noinput

# Strong sanity print: confirms vendor + host + db name Django is using
python manage.py shell -c "from django.db import connection; print('DB_VENDOR=', connection.vendor); print('DB_HOST=', connection.settings_dict.get('HOST')); print('DB_NAME=', connection.settings_dict.get('NAME'))"

# Start server
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -