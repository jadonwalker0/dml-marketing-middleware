#!/usr/bin/env bash
set -euo pipefail

echo "Starting DML Marketing Middleware..."

# Navigate to app directory
if [ -f /home/site/wwwroot/manage.py ]; then
  cd /home/site/wwwroot
else
  echo "ERROR: manage.py not found"
  exit 1
fi

echo "Running in: $(pwd)"
echo "Database: MySQL on Azure"

# Activate virtual environment if it exists
if [ -d "antenv" ]; then
  source antenv/bin/activate
  echo "Activated antenv virtual environment"
fi

python -V

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

# Display database connection info (without password)
python manage.py shell -c "from django.conf import settings; db = settings.DATABASES['default']; print(f\"Database: {db['ENGINE']} @ {db['HOST']}:{db['PORT']}/{db['NAME']}\")"

# Start worker in background
echo "Starting Lead Processing Worker..."
python workers/process_leads.py &

# Start Gunicorn in foreground
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -