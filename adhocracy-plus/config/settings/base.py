"""Django settings for adhocracy+."""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from django.conf import locale
from django.utils.translation import ugettext_lazy as _

CONFIG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(CONFIG_DIR)
BASE_DIR = os.path.dirname(PROJECT_DIR)

# General settings
CONTACT_EMAIL = 'contact@domain'

# Application definition

INSTALLED_APPS = (

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
    'rest_framework.authtoken',
    'django_filters',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rules.apps.AutodiscoverRulesConfig',
    'easy_thumbnails',
    'ckeditor',
    'ckeditor_uploader',
    'capture_tag',
    'background_task',
    'parler',

    # Wagtail cms components
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.contrib.settings',
    'wagtail.contrib.styleguide',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',
    'modelcluster',
    'taggit',
    'apps.cms.pages',
    'apps.cms.settings',
    'apps.cms.contacts',
    'apps.cms.news',
    'apps.cms.use_cases',
    'apps.cms.images',

    # General adhocracy 4 components
    'adhocracy4.actions',
    'adhocracy4.administrative_districts',
    'adhocracy4.categories',
    'adhocracy4.ckeditor',
    'adhocracy4.comments',
    'adhocracy4.comments_async',
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
    'apps.actions',
    'apps.captcha',
    'apps.contrib',
    'apps.interactiveevents',
    'apps.likes',
    'apps.maps',
    'apps.moderatorfeedback',
    'apps.moderatorremark',
    'apps.newsletters',
    'apps.notifications',
    'apps.organisations',
    'apps.questions',
    'apps.users',

    # General apps containing views
    'apps.account',
    'apps.dashboard',
    'apps.embed',
    'apps.exports',
    'apps.offlineevents',
    'apps.projects',

    # Apps defining phases
    'apps.activities',
    'apps.budgeting',
    'apps.documents',
    'apps.ideas',
    'apps.mapideas',
    'apps.polls',
    'apps.topicprio',
    'apps.debate'
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django_samesite_none.middleware.SameSiteNoneMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
    'django_cloudflare_push.middleware.push_middleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'apps.embed.middleware.AjaxPathMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
)

ROOT_URLCONF = 'adhocracy-plus.config.urls'

LOCALE_PATHS = [
    # use the first line in branches and forks to keep the original translations
    # from main branch and overwrite or add extra translations in fork

    # os.path.join(BASE_DIR, 'locale-fork/locale'),
    os.path.join(BASE_DIR, 'locale-source/locale')
]

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

WSGI_APPLICATION = 'adhocracy-plus.config.wsgi.application'


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

LANGUAGE_CODE = 'en'
DEFAULT_USER_LANGUAGE_CODE = 'de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ('en', _('English')),
    ('de', _('German')),
    ('nl', _('Dutch')),
    ('ky', _('Kyrgyz')),
    ('ru', _('Russian'))
]

# adding language info for ky
EXTRA_LANG_INFO = {
    'ky': {
        'bidi': False,
        'code': 'ky',
        'name': 'Kyrgyz',
        'name_local': u"Кыргызча",
    },
}
LANG_INFO = dict(locale.LANG_INFO, **EXTRA_LANG_INFO)
locale.LANG_INFO = LANG_INFO

PARLER_LANGUAGES = {
    1: [{'code': language_code} for language_code, language in LANGUAGES],
    'default': {'fallbacks': ['en', 'de'],
                }
}

PARLER_ENABLE_CACHING = False

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
    'eventimage': {'min_resolution': (500, 600)},
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

AUTH_USER_MODEL = 'a4_candy_users.User'

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_ADAPTER = 'apps.users.adapters.AccountAdapter'
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_FORMS = {'signup': 'apps.users.forms.DefaultSignupForm',
                 'login': 'apps.users.forms.DefaultLoginForm'}
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 10
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300  # seconds
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_USERNAME_MIN_LENGTH = 5
ACCOUNT_USERNAME_REQUIRED = True
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_FORMS = {'signup': 'apps.users.forms.SocialTermsSignupForm'}
SOCIALACCOUNT_QUERY_EMAIL = True

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = '/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

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
        'title': _('Rich text editor'),
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['Image'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['CollapsibleItem'],
            ['Embed', 'EmbedBase']
        ],
        'removePlugins': 'stylesheetparser',
        'extraAllowedContent': 'iframe[*]; div[*]',
    },
    'video-editor': {
        'width': '100%',
        'title': _('Rich text editor'),
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Embed', 'EmbedBase']
        ],
        'removePlugins': 'stylesheetparser',
        'extraAllowedContent': 'iframe[*]; div[*]',
    }
}

BLEACH_LIST = {
    'default' : {
        'tags': ['p','strong','em','u','ol','li','ul','a'],
        'attributes': {
            'a': ['href', 'rel', 'target'],
        },
    },
    'image-editor': {
        'tags': ['p','strong','em','u','ol','li','ul','a','img'],
        'attributes': {
            'a': ['href', 'rel', 'target'],
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
                 'div', 'iframe'],
        'attributes': {
            'a': ['href', 'rel', 'target'],
            'img': ['src', 'alt', 'style'],
            'div': ['class'],
            'iframe': ['src', 'alt', 'style']
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
    'video-editor': {
        'tags': ['a', 'img', 'div', 'iframe'],
        'attributes': {
            'a': ['href', 'rel', 'target'],
            'img': ['src', 'alt', 'style'],
            'div': ['class'],
            'iframe': ['src', 'alt', 'style']
        }
    }
}

# Wagtail
WAGTAIL_SITE_NAME = 'adhocracy+'
WAGTAILIMAGES_IMAGE_MODEL = 'a4_candy_cms_images.CustomImage'

WAGTAILADMIN_RICH_TEXT_EDITORS = {
    'default': {
        'WIDGET': 'wagtail.admin.rich_text.HalloRichTextArea'
    }
}

# adhocracy4

A4_ORGANISATIONS_MODEL = 'a4_candy_organisations.Organisation'

A4_RATEABLES = (
    ('a4comments', 'comment'),
    ('a4_candy_ideas', 'idea'),
    ('a4_candy_mapideas', 'mapidea'),
    ('a4_candy_budgeting', 'proposal'),
    ('a4_candy_topicprio', 'topic'),
)

A4_COMMENTABLES = (
    ('a4comments', 'comment'),
    ('a4_candy_ideas', 'idea'),
    ('a4_candy_documents', 'chapter'),
    ('a4_candy_documents', 'paragraph'),
    ('a4_candy_mapideas', 'mapidea'),
    ('a4_candy_budgeting', 'proposal'),
    ('a4_candy_polls', 'poll'),
    ('a4_candy_topicprio', 'topic'),
    ('a4_candy_debate', 'subject')
)

A4_COMMENT_CATEGORIES = (
    ('sug', _('suggestion')),
    ('not', _('note')),
    ('que', _('question'))
)

A4_REPORTABLES = (
    ('a4comments', 'comment'),
    ('a4_candy_ideas', 'idea'),
    ('a4_candy_mapideas', 'mapidea'),
    ('a4_candy_budgeting', 'proposal'),
)

A4_ACTIONABLES = (
    ('a4comments', 'comment'),
    ('a4_candy_ideas', 'idea'),
    ('a4_candy_budgeting', 'proposal'),
    ('a4_candy_mapideas', 'mapidea'),
)

A4_AUTO_FOLLOWABLES = (
    ('a4comments', 'comment'),
    ('a4_candy_ideas', 'idea'),
    ('a4_candy_mapideas', 'mapidea'),
    ('a4_candy_budgeting', 'proposal'),
    ('a4_candy_polls', 'vote'),
)

A4_CATEGORIZABLE = (
    ('a4_candy_ideas', 'idea'),
    ('a4_candy_mapideas', 'mapidea'),
    ('a4_candy_budgeting', 'proposal'),
    ('a4_candy_topicprio', 'topic'),
)

A4_LABELS_ADDABLE = (
    ('a4_candy_ideas', 'idea'),
    ('a4_candy_mapideas', 'mapidea'),
    ('a4_candy_budgeting', 'proposal'),
    ('a4_candy_topicprio', 'topic'),
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
    'PROJECT_DASHBOARD_CLASS': 'apps.dashboard.ProjectDashboard',
    'BLUEPRINTS': 'apps.dashboard.blueprints.blueprints'
}

A4_PROJECT_TOPICS = (
    ('ANT', _('Anti-discrimination')),
    ('WOR', _('Work & economy')),
    ('BUI', _('Building & living')),
    ('EDU', _('Education & research')),
    ('CHI', _('Children, youth & family')),
    ('FIN', _('Finances')),
    ('HEA', _('Health & sports')),
    ('INT', _('Integration')),
    ('CUL', _('Culture & leisure')),
    ('NEI', _('Neighborhood & participation')),
    ('URB', _('Urban development')),
    ('ENV', _('Environment & public green space')),
    ('TRA', _('Traffic'))
)

A4_ACTIONS_PHASE_ENDS_HOURS = 48

# Disable CSP by default
CSP_REPORT_ONLY = True
CSP_DEFAULT_SRC = ["'self'", "'unsafe-inline'", "'unsafe-eval'", 'data:', 'blob:', '*']

SITE_ID = 1 # overwrite this in local.py if needed
