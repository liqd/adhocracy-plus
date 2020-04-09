from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

for template_engine in TEMPLATES:
    template_engine['OPTIONS']['debug'] = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k3l^@x53$l5@y(fo6ivgplj&q^^rmtl^enzse5ozxuepx0$s()'

try:
    import debug_toolbar
except ImportError:
    pass
else:
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

    INTERNAL_IPS = ('127.0.0.1', 'localhost')

try:
    from .local import *
except ImportError:
    pass

try:
    INSTALLED_APPS += tuple(ADDITIONAL_APPS)
except NameError:
    pass

BASE_URL = 'http://localhost:8004'
CAPTCHA_URL = 'https://captcheck.netsyms.com/api.php'
SITE_ID = 1
