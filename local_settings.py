# Import everything from the main settings first
from config.settings import *

# Override only what we need for local development
SECRET_KEY = "temp-local-key-for-migrations"
DEBUG = True

# Use SQLite locally (easier than MySQL on Windows)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "temp_local.db",
    }
}

# Disable Service Bus requirement locally
SERVICEBUS_CONNECTION_STRING = ""