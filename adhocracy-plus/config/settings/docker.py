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


# Instance-specific settings, rendered by Salt into a .env file inside the
# named volume mounted at /data (docker-compose.yml). The .env format is kept
# as-is (APLUS_CONFIG / APLUS_SOCIAL_ACCOUNTS / APLUS_SENTRY_URL). Coolify
# overrides container env vars, so the file is read directly instead of via
# os.environ.
import json
import os

from dotenv import dotenv_values

_APLUS_INSTANCE_ENV = dotenv_values("/data/.env") or {}


def _load_json_value(name, default="{}"):
    raw = _APLUS_INSTANCE_ENV.get(name)
    if not raw:
        return json.loads(default)
    return json.loads(raw)


_instance = _load_json_value("APLUS_CONFIG")
globals().update(_instance)

if _APLUS_INSTANCE_ENV.get("APLUS_SOCIAL_ACCOUNTS"):
    SOCIALACCOUNT_PROVIDERS = json.loads(_APLUS_INSTANCE_ENV["APLUS_SOCIAL_ACCOUNTS"])

if _APLUS_INSTANCE_ENV.get("APLUS_SENTRY_URL"):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=_APLUS_INSTANCE_ENV["APLUS_SENTRY_URL"],
        integrations=[DjangoIntegration()],
        release=os.environ.get("GITREF", ""),
    )
