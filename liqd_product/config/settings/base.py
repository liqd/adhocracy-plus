"""Django settings for Beteiligung.in."""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from django.utils.translation import ugettext_lazy as _

CONFIG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(CONFIG_DIR)
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Application definition

INSTALLED_APPS = (

    # Watch out this needs to be included first
    'liqd_product.apps.django_overwrites',

    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'widget_tweaks',
    'rest_framework',
    'allauth',
    'allauth.account',
    'rules.apps.AutodiscoverRulesConfig',
    'easy_thumbnails',
    'ckeditor',
    'ckeditor_uploader',
    'capture_tag',
    'background_task',

    # Wagtail cms components
    'wagtail.contrib.settings',
    'wagtail.wagtailforms',
    'wagtail.wagtailredirects',
    'wagtail.wagtailembeds',
    'wagtail.wagtailsites',
    'wagtail.wagtailusers',
    'wagtail.wagtailsnippets',
    'wagtail.wagtaildocs',
    'wagtail.wagtailimages',
    'wagtail.wagtailsearch',
    'wagtail.wagtailadmin',
    'wagtail.wagtailcore',
    'wagtail.contrib.wagtailstyleguide',
    'modelcluster',
    'taggit',
    'liqd_product.apps.cms.pages',
    'liqd_product.apps.cms.settings',

    # General adhocracy 4 components
    'adhocracy4.actions',
    'adhocracy4.administrative_districts',
    'adhocracy4.categories',
    'adhocracy4.ckeditor',
    'adhocracy4.comments',
    'adhocracy4.dashboard',
    'adhocracy4.filters',
    'adhocracy4.follows',
    'adhocracy4.forms',
    'adhocracy4.images',
    'adhocracy4.labels',
    'adhocracy4.maps',
    'adhocracy4.modules',
    'adhocracy4.organisations',
    'adhocracy4.phases',
    'adhocracy4.projects',
    'adhocracy4.ratings',
    'adhocracy4.reports',
    'adhocracy4.rules',

    # General components that define models or helpers
    'liqd_product.apps.contrib',
    'liqd_product.apps.organisations',
    'liqd_product.apps.partners',
    'liqd_product.apps.users',
    'meinberlin.apps.actions',
    'meinberlin.apps.contrib',
    'meinberlin.apps.maps',
    'meinberlin.apps.moderatorfeedback',
    'meinberlin.apps.moderatorremark',
    'meinberlin.apps.notifications',

    # General apps containing views
    'liqd_product.apps.account',
    'liqd_product.apps.dashboard',
    'meinberlin.apps.embed',
    'meinberlin.apps.offlineevents',
    'meinberlin.apps.projects',

    # Apps defining phases
    'meinberlin.apps.activities',
    'meinberlin.apps.documents',
    'meinberlin.apps.ideas',
    'meinberlin.apps.mapideas',
    'meinberlin.apps.polls',
    'meinberlin.apps.budgeting',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_cloudflare_push.middleware.push_middleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'liqd_product.apps.partners.middleware.PartnerMiddleware',
    'meinberlin.apps.embed.middleware.AjaxPathMiddleware',
    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
)

SITE_ID = 1

ROOT_URLCONF = 'liqd_product.config.urls'

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings'
            ],
        },
    },
]

WSGI_APPLICATION = 'liqd_product.config.wsgi.application'

REVERSE_METHOD = 'liqd_product.apps.partners.urlresolvers.reverse'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'TEST': {
            'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
        }
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'de-DE'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

IMAGE_ALIASES = {
    '*': {
        'max_size': 5*10**6,
        'fileformats': ('image/png', 'image/jpeg', 'image/gif')
    },
    'heroimage': {'min_resolution': (1500, 500)},
    'tileimage': {'min_resolution': (500, 300)},
    'logo': {'min_resolution': (200, 200), 'aspect_ratio': (1, 1)},
    'avatar': {'min_resolution': (200, 200)},
    'idea_image': {'min_resolution': (600, 400)},
}

THUMBNAIL_ALIASES = {
    '': {
        'heroimage': {'size': (1500, 500), 'crop': 'smart'},
        'heroimage_preview': {'size': (880, 220), 'crop': 'smart'},
        'project_thumbnail': {'size': (520, 330), 'crop': 'smart'},
        'idea_image': {'size': (800, 0), 'crop': 'scale'},
        'idea_thumbnail': {'size': (240, 240), 'crop': 'smart'},
        'avatar': {'size': (200, 200), 'crop': 'smart'},
        'item_image': {'size': (330, 0), 'crop': 'scale'},
        'map_thumbnail': {'size': (200, 200), 'crop': 'smart'}
    }
}

ALLOWED_UPLOAD_IMAGES = ('png', 'jpeg', 'gif')


# Authentication

AUTH_USER_MODEL = 'liqd_product_users.User'

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_ADAPTER = 'liqd_product.apps.users.adapters.AccountAdapter'
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 10
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300  # seconds
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_SIGNUP_FORM_CLASS = 'liqd_product.apps.users.forms.TermsSignupForm'
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = '/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# CKEditor

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_RESTRICT_BY_USER = 'username'
CKEDITOR_ALLOW_NONIMAGE_FILES = True

CKEDITOR_CONFIGS = {
    'default': {
        'width': '100%',
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink']
        ]
    },
    'image-editor': {
        'width': '100%',
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['Image'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink']
        ]
    },
    'collapsible-image-editor': {
        'width': '100%',
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['Image'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['CollapsibleItem']
        ]
    }
}

BLEACH_LIST = {
    'default' : {
        'tags': ['p','strong','em','u','ol','li','ul','a'],
        'attributes': {
            'a': ['href', 'rel'],
        },
    },
    'image-editor': {
        'tags': ['p','strong','em','u','ol','li','ul','a','img'],
        'attributes': {
            'a': ['href', 'rel'],
            'img': ['src', 'alt', 'style']
        },
        'styles': [
            'float',
            'margin',
            'padding',
            'width',
            'height',
            'margin-bottom',
            'margin-top',
            'margin-left',
            'margin-right',
        ],
    },
    'collapsible-image-editor': {
        'tags': ['p', 'strong', 'em', 'u', 'ol', 'li', 'ul', 'a', 'img',
                 'div'],
        'attributes': {
            'a': ['href', 'rel'],
            'img': ['src', 'alt', 'style'],
            'div': ['class']
        },
        'styles': [
            'float',
            'margin',
            'padding',
            'width',
            'height',
            'margin-bottom',
            'margin-top',
            'margin-left',
            'margin-right',
        ],
    }
}

# Wagtail
WAGTAIL_SITE_NAME = 'Beteiligung.in'

# adhocracy4

A4_ORGANISATIONS_MODEL = 'liqd_product_organisations.Organisation'

A4_RATEABLES = (
    ('a4comments', 'comment'),
    ('meinberlin_ideas', 'idea'),
    ('meinberlin_mapideas', 'mapidea'),
    ('meinberlin_budgeting', 'proposal'),
)

A4_COMMENTABLES = (
    ('a4comments', 'comment'),
    ('meinberlin_ideas', 'idea'),
    ('meinberlin_documents', 'chapter'),
    ('meinberlin_documents', 'paragraph'),
    ('meinberlin_mapideas', 'mapidea'),
    ('meinberlin_budgeting', 'proposal'),
    ('meinberlin_polls', 'poll'),
)

A4_REPORTABLES = (
    ('a4comments', 'comment'),
    ('meinberlin_ideas', 'idea'),
    ('meinberlin_mapideas', 'mapidea'),
    ('meinberlin_budgeting', 'proposal'),
)

A4_ACTIONABLES = (
    ('a4comments', 'comment'),
    ('meinberlin_ideas', 'idea'),
    ('meinberlin_budgeting', 'proposal'),
    ('meinberlin_mapideas', 'mapidea'),
)

A4_AUTO_FOLLOWABLES = (
    # Disabled to keep current behaviour: the auto follow functionality did
    # not work until 2018/03/21 due to a adhocracy4 bug
    # ('a4comments', 'comment'),
    # ('meinberlin_ideas', 'idea'),
    # ('meinberlin_mapideas', 'mapidea'),
)

A4_CATEGORIZABLE = (
    ('meinberlin_ideas', 'idea'),
    ('meinberlin_mapideas', 'mapidea'),
    ('meinberlin_budgeting', 'proposal'),
)

A4_LABELS_ADDABLE = (
    ('meinberlin_ideas', 'idea'),
    ('meinberlin_mapideas', 'mapidea'),
    ('meinberlin_budgeting', 'proposal'),
)

A4_CATEGORY_ICONS = (
    ('', _('Pin without icon')),
    ('diamant', _('Diamond')),
    ('dreieck_oben', _('Triangle up')),
    ('dreieck_unten', _('Triangle down')),
    ('ellipse', _('Ellipse')),
    ('halbkreis', _('Semi circle')),
    ('hexagon', _('Hexagon')),
    ('parallelogramm', _('Rhomboid')),
    ('pentagramm', _('Star')),
    ('quadrat', _('Square')),
    ('raute', _('Octothorpe')),
    ('rechtecke', _('Rectangle')),
    ('ring', _('Circle')),
    ('rw_dreieck', _('Right triangle')),
    ('zickzack', _('Zigzag'))
)


A4_MAP_BASEURL = 'https://{s}.tile.openstreetmap.org/'
A4_MAP_ATTRIBUTION = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
A4_MAP_BOUNDING_BOX = ([[54.983, 15.016], [47.302, 5.988]])

A4_DASHBOARD = {
    'PROJECT_DASHBOARD_CLASS': 'meinberlin.apps.dashboard.ProjectDashboard',
    'BLUEPRINTS': 'liqd_product.apps.dashboard.blueprints.blueprints'
}

CONTACT_EMAIL = 'support-beteiligung@liqd.net'

# The default language is used for emails and strings
# that are stored translated to the database.
DEFAULT_LANGUAGE = 'de'
