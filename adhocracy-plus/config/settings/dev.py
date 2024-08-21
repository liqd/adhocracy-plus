from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

for template_engine in TEMPLATES:
    template_engine["OPTIONS"]["debug"] = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

try:
    import debug_toolbar
except ImportError:
    pass
else:
    INSTALLED_APPS += ("debug_toolbar",)
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

    INTERNAL_IPS = ("127.0.0.1", "localhost")

WAGTAILADMIN_BASE_URL = "http://localhost:8004"
CAPTCHA_URL = "https://captcheck.netsyms.com/api.php"
SITE_ID = 1

if os.getenv("DATABASE") == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "django",
            "USER": "django",
            "PASSWORD": "",
            "HOST": "",
            "PORT": "5556",
            "OPTIONS": {},
        }
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        # Define a handler that prints logs to the console (terminal)
        "console": {
            "level": "INFO",  # Set the level to INFO to print info and debug messages
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        # Define a logger for your Django app (replace 'yourapp' with your app name)
        "apps.fairvote": {
            "handlers": ["console"],
            "level": "INFO",  # Set the level to DEBUG to print debug messages
            "propagate": True,
        },
        "apps.fairvote2": {
            "handlers": ["console"],
            "level": "DEBUG",  # Set the level to DEBUG to print debug messages
            "propagate": True,
        },
    },
}

CELERY_TASK_ALWAYS_EAGER = True

# The local.py import happens at the end of this file so that it can overwrite
# any defaults in dev.py.
# Special cases are:
# 1) ADDITIONAL_APPS in local.py should be appended to INSTALLED_APPS.
# 2) CKEDITOR_URL should be inserted into CKEDITOR_CONFIGS in the correct location.

"""
try:
    from .local import *
except ImportError:
    pass
"""
try:
    INSTALLED_APPS += tuple(ADDITIONAL_APPS)
except NameError:
    pass

try:
    CKEDITOR_CONFIGS["collapsible-image-editor"]["embed_provider"] = CKEDITOR_URL
    CKEDITOR_CONFIGS["video-editor"]["embed_provider"] = CKEDITOR_URL
except NameError:
    pass
