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
    "publish-results-reminders-hourly": {
        "task": "send_publish_results_reminders",
        "schedule": timedelta(hours=1),
        "args": (),
    },
    "send-recently-started-project-notifications": {
        "task": "send_recently_started_project_notifications",
        # Coverage window is NOTIFICATION_PROJECT_STARTED_HOURS (default 72h);
        # the tasks deduplicate, so frequent runs are safe and each project is
        # notified exactly once.
        "schedule": timedelta(days=1),
    },
    "send-recently-completed-project-notifications": {
        "task": "send_recently_completed_project_notifications",
        # Coverage window is NOTIFICATION_PROJECT_COMPLETED_HOURS (default 72h).
        "schedule": timedelta(days=1),
    },
    "send_upcoming-event-notifications": {
        "task": "send_upcoming_event_notifications",
        # Coverage window is NOTIFICATION_EVENT_STARTING_HOURS (default 72h).
        "schedule": timedelta(days=1),
    },
    "refresh_project_summaries": {
        "task": "refresh_project_summaries",
        "schedule": timedelta(minutes=30),
    },
}

ALLOWED_HOSTS = ["*"]

WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL", "http://localhost:8004")


# Instance-specific settings, JSON-encoded by Salt in the env_file
# (/data/docker/adhocracy-plus/.env on conway). Copy of the old
# local.py content, delivered via env vars instead of a mounted file.
import json


def _load_json_env(name, default=""):
    raw = os.environ.get(name)
    if not raw:
        return json.loads(default)
    return json.loads(raw)


_instance = _load_json_env("APLUS_CONFIG", "{}")
globals().update(_instance)

if "APLUS_SOCIAL_ACCOUNTS" in os.environ:
    SOCIALACCOUNT_PROVIDERS = json.loads(os.environ["APLUS_SOCIAL_ACCOUNTS"])

if "APLUS_SENTRY_URL" in os.environ and os.environ["APLUS_SENTRY_URL"]:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=os.environ["APLUS_SENTRY_URL"],
        integrations=[DjangoIntegration()],
        release=os.environ.get("GITREF", ""),
    )
