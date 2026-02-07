#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

# Optional one-time superuser creation (controlled by env vars)
if [ "$DJANGO_CREATE_SUPERUSER" = "1" ]; then
  echo "Creating superuser (one-time)..."
  python manage.py shell -c "import os; from django.contrib.auth import get_user_model; User=get_user_model(); u=os.environ.get('DJANGO_SUPERUSER_USERNAME'); e=os.environ.get('DJANGO_SUPERUSER_EMAIL'); p=os.environ.get('DJANGO_SUPERUSER_PASSWORD'); \
print('Missing env vars') if not (u and e and p) else (User.objects.filter(username=u).exists() or User.objects.create_superuser(u,e,p))"
fi

echo "Starting gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000
