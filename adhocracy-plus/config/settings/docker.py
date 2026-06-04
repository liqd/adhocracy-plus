import os
from datetime import timedelta

from .dev import *

# PostgreSQL with PostGIS (service name "db" in docker-compose)
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("POSTGRES_DB", "django"),
        "USER": os.environ.get("POSTGRES_USER", "django"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "django"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_TASK_ALWAYS_EAGER = False

CELERY_BEAT_SCHEDULE = {
    "send-recently-started-project-notifications": {
        "task": "send_recently_started_project_notifications",
        "schedule": timedelta(days=3),
    },
    "send-recently-completed-project-notifications": {
        "task": "send_recently_completed_project_notifications",
        "schedule": timedelta(days=3),
    },
    "send_upcoming-event-notifications": {
        "task": "send_upcoming_event_notifications",
        "schedule": timedelta(days=3),
    },
}

ALLOWED_HOSTS = ["*"]

WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "http://localhost:8004")
