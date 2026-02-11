#!/usr/bin/env bash
set -euo pipefail

echo "PWD=$(pwd)"
echo "PYTHON=$(which python || true)"
python --version || true

echo "Running migrate..."
python manage.py migrate --noinput

echo "Starting gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
