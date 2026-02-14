##!/usr/bin/env bash
set -euo pipefail

echo "Starting DML Marketing Middleware..."
cd /home/site/wwwroot

echo "Running in: $(pwd)"
python --version

# Verify packages are installed
echo "Checking Django installation..."
python -c "import django; print('Django version:', django.get_version())" || {
    echo "ERROR: Django not found! Installing dependencies..."
    pip install -r requirements.txt
}

echo "Running migrations..."
python manage.py migrate --fake-initial --noinput

# Create superuser
if [ "${DJANGO_CREATE_SUPERUSER:-0}" = "1" ]; then
  python manage.py shell <<'EOF'
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "changeme")
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created")
EOF
fi

echo "Starting Lead Processing Worker..."
python workers/process_leads.py &

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 --access-logfile - --error-logfile -