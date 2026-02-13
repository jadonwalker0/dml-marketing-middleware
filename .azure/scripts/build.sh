#!/bin/bash
set -e

echo "=== Custom Build Script ==="
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "=== Running Django migrations ==="
python manage.py migrate --noinput

echo "=== Creating superuser if needed ==="
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
else:
    print(f"Superuser '{username}' already exists")
EOF
fi

echo "=== Build complete ==="
```

---

### STEP 3: Update Azure App Setting

**Azure Portal → middleware-api → Configuration → Application settings**

**Find or add:**
```
Name: PRE_BUILD_COMMAND
Value: chmod +x .azure/scripts/build.sh && .azure/scripts/build.sh