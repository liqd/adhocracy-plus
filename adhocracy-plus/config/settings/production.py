from datetime import timedelta

from .base import *

DEBUG = False

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

try:
    from .local import *
except ImportError:
    pass

try:
    from .polygons import *
except ImportError:
    pass

try:
    INSTALLED_APPS += tuple(ADDITIONAL_APPS)
except NameError:
    pass

try:
    CKEDITOR_CONFIGS["collapsible-image-editor"]["embed_provider"] = CKEDITOR_URL
    CKEDITOR_CONFIGS["video-editor"]["embed_provider"] = CKEDITOR_URL
except NameError:
    pass

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
}
