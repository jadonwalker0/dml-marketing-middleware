#!/usr/bin/env bash
set -e

# Prefer persistent app path if it exists
if [ -f /home/site/app/manage.py ]; then
  cd /home/site/app
else
  # Oryx usually sets APP_PATH. Fall back to the latest extracted folder.
  if [ -n "$APP_PATH" ] && [ -f "$APP_PATH/manage.py" ]; then
    cd "$APP_PATH"
  else
    cd "$(ls -td /tmp/8de* 2>/dev/null | head -1)"
  fi
fi

echo "Running in: $(pwd)"
PYBIN="$(command -v python || command -v python3)"
echo "Using: $PYBIN"
$PYBIN -V

$PYBIN manage.py migrate --noinput

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --error-logfile -