#!/usr/bin/env bash
set -euo pipefail

echo "Starting DML Marketing Middleware..."

# Navigate to app directory
cd /home/site/wwwroot

echo "Running in: $(pwd)"
echo "Database: MySQL on Azure"
python -V

# Activate virtual environment if it exists
if [ -d "/home/site/wwwroot/antenv" ]; then
    source /home/site/wwwroot/antenv/bin/activate
fi

# Install dependencies if not already installed
if ! python -c "import django" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt --break-system-packages
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser if environment variables are set
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

# Display database connection info
python manage.py shell -c "from django.conf import settings; db = settings.DATABASES['default']; print(f\"Database: {db['ENGINE']} @ {db['HOST']}:{db['PORT']}/{db['NAME']}\")"

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info