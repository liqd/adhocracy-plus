from celery.schedules import crontab

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
    "send-recently-started-project-notifications": {
        "task": "send_recently_started_project_notifications",
        "schedule": crontab.from_string("0 0 */3 * *"),
    },
    "send-recently-completed-project-notifications": {
        "task": "send_recently_completed_project_notifications",
        "schedule": crontab.from_string("0 0 */3 * *"),
    },
    "send_upcoming-event-notifications": {
        "task": "send_upcoming_event_notifications",
        "schedule": crontab.from_string("0 0 */3 * *"),
    },
}
