"""
Django settings for DML Marketing Middleware project.
Configured for Azure MySQL Database.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security Settings
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY environment variable is not set")

DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"

# Allowed Hosts
allowed_hosts_env = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(",") if h.strip()]

# Always allow localhost for development
ALLOWED_HOSTS += ["localhost", "127.0.0.1"]

# Azure-specific hosts
ALLOWED_HOSTS += [
    "middleware-api-fagee5h3hzbtftca.eastus2-01.azurewebsites.net",
    # Azure health check IPs
    "169.254.129.1", "169.254.129.2", "169.254.129.3", "169.254.129.4",
]

# Allow all hosts in Azure if needed (for initial setup)
if os.getenv("AZURE_ALLOW_ALL_HOSTS", "0") == "1":
    ALLOWED_HOSTS = ["*"]


# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    "https://middleware-api-fagee5h3hzbtftca.eastus2-01.azurewebsites.net",
]

# Proxy settings for Azure
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Security settings for production
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = False  # Azure handles this


# Application definition
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps
    "core",
    "leads",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database - Azure MySQL
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Get MySQL connection details from environment variables
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

# Validate required MySQL settings
if not all([MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD]):
    raise RuntimeError(
        "MySQL configuration incomplete. Required environment variables: "
        "MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD"
    )

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": MYSQL_HOST,
        "PORT": MYSQL_PORT,
        "NAME": MYSQL_DATABASE,
        "USER": MYSQL_USER,
        "PASSWORD": MYSQL_PASSWORD,
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
            # SSL settings for Azure MySQL (recommended)
            "ssl": {
                "ssl-mode": "required"
            } if os.getenv("MYSQL_SSL", "1") == "1" else {},
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "leads": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# Azure Service Bus Configuration
SERVICEBUS_CONNECTION_STRING = os.getenv("SERVICEBUS_CONNECTION_STRING", "")
SERVICEBUS_QUEUE_NAME = os.getenv("SERVICEBUS_QUEUE_NAME", "webform-leads")


# Total Expert API Configuration
TOTAL_EXPERT_CLIENT_ID = os.getenv("TOTAL_EXPERT_CLIENT_ID", "")
TOTAL_EXPERT_CLIENT_SECRET = os.getenv("TOTAL_EXPERT_CLIENT_SECRET", "")
TOTAL_EXPERT_API_URL = os.getenv("TOTAL_EXPERT_API_URL", "https://api.totalexpert.net")

JAZZMIN_SETTINGS = {
    # Title in the browser tab
    "site_title": "DML Marketing Admin",

    # Title on the login screen and top of sidebar
    "site_header": "Direct Mortgage Loans",

    # Brand text in the top-left of the sidebar
    "site_brand": "DML Marketing",

    # Welcome text on the login screen
    "welcome_sign": "Welcome to the DML Marketing Middleware",

    # Copyright footer
    "copyright": "Direct Mortgage Loans",

    # Top nav links
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "leads.LeadSubmission"},
        {"model": "core.LoanOfficer"},
    ],

    # Sidebar icons — using Font Awesome classes
    "icons": {
        "auth":                     "fas fa-users-cog",
        "auth.user":                "fas fa-user",
        "auth.Group":               "fas fa-users",
        "core.LoanOfficer":         "fas fa-id-badge",
        "leads.LeadSubmission":     "fas fa-funnel-dollar",
        "directory.LoanOfficer":    "fas fa-address-card",
    },

    "default_icon_parents":  "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    # Sidebar is expanded by default
    "navigation_expanded": True,
    "show_sidebar": True,

    # Order apps in the sidebar
    "order_with_respect_to": ["leads", "core", "directory", "auth"],

    # Opens related models in a modal popup instead of new page
    "related_modal_active": True,

    # Show the UI builder toggle in the top bar (great for live tweaking)
    "show_ui_builder": True,

    # Use the search bar on list views
    "search_model": ["leads.LeadSubmission", "core.LoanOfficer"],
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",          # Clean, professional Bootstrap theme
    "dark_mode_theme": "darkly", # Auto dark mode when OS is dark
    "button_classes": {
        "primary":   "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info":      "btn-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
}