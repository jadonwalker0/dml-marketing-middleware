#!/usr/bin/env bash
set -euo pipefail

echo "Starting DML Marketing Middleware..."

# Navigate to app directory
cd /home/site/wwwroot

echo "Running in: $(pwd)"
echo "Python version:"
python -V

# Find and activate the virtual environment that Azure creates
if [ -d "antenv" ]; then
    echo "Activating antenv..."
    source antenv/bin/activate
elif [ -d "/home/site/wwwroot/antenv" ]; then
    echo "Activating /home/site/wwwroot/antenv..."
    source /home/site/wwwroot/antenv/bin/activate
else
    echo "No virtual environment found, installing packages globally..."
    pip install -r requirements.txt --break-system-packages
fi

# Verify Django is available
python -c "import django; print(f'Django version: {django.get_version()}')"

echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser
if [ -n "${DJANGO_CREATE_SUPERUSER:-}" ] && [ "${DJANGO_CREATE_SUPERUSER}" = "1" ]; then
  echo "Checking for superuser..."
  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = "${DJANGO_SUPERUSER_USERNAME:-admin}"
email = "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
password = "${DJANGO_SUPERUSER_PASSWORD:-changeme}"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created successfully")
else:
    print(f"Superuser '{username}' already exists")
EOF
fi

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info