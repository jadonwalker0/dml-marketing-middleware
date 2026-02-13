"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""
# path to this file: "dml-marketing-middleware/config/>file<"

import logging
import os
from django.core.wsgi import get_wsgi_application
from django.db import connection

# Force the correct settings module no matter what Azure/env is doing
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

application = get_wsgi_application()

logger = logging.getLogger(__name__)
logger.warning("WEB DB: %s %s %s",
               connection.vendor,
               connection.settings_dict.get("HOST"),
               connection.settings_dict.get("NAME"))