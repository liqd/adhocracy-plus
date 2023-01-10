from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

for template_engine in TEMPLATES:
    template_engine["OPTIONS"]["debug"] = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "k3l^@x53$l5@y(fo6ivgplj&q^^rmtl^enzse5ozxuepx0$s()"

try:
    import debug_toolbar
except ImportError:
    pass
else:
    INSTALLED_APPS += ("debug_toolbar",)
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

    INTERNAL_IPS = ("127.0.0.1", "localhost")

try:
    from .local import *
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


WAGTAILADMIN_BASE_URL = "http://localhost:8004"
CAPTCHA_URL = "https://captcheck.netsyms.com/api.php"
SITE_ID = 1

if os.getenv("DATABASE") == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "django",
            "USER": "django",
            "PASSWORD": "",
            "HOST": "",
            "PORT": "5556",
            "OPTIONS": {},
        }
    }
