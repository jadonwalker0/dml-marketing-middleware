#!/usr/bin/env bash
set -euo pipefail

echo "PWD=$(pwd)"
echo "PY=$(which python || true)"
python --version || true

# quick sanity checks
python -c "import django; print('DJANGO_OK', django.get_version())"

# show DB + LO slugs
python manage.py shell -c "from django.conf import settings; from directory.models import LoanOfficer; print('RUNTIME_DB=', settings.DATABASES['default']['NAME']); print('RUNTIME_LO_COUNT=', LoanOfficer.objects.count()); print('RUNTIME_LO_SLUGS=', list(LoanOfficer.objects.values_list('slug', flat=True)) )"

# migrate + run server
# note adding for commit
python manage.py migrate --noinput
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --error-logfile -