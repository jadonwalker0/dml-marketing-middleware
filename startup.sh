#!/bin/bash
set -e

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
gunicorn dml-marketing-middleware --bind 0.0.0.0:8000