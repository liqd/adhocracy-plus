"""Django settings for adhocracy+."""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from datetime import timedelta

from django.conf import locale
from django.utils.translation import gettext_lazy as _

CONFIG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(CONFIG_DIR)
BASE_DIR = os.path.dirname(PROJECT_DIR)

# General settings
CONTACT_EMAIL = "contact@domain"

# Link to a dokuwiki instance containing a manual for aplus
# Leave blank to disable
APLUS_MANUAL_URL = ""

# Application definition

INSTALLED_APPS = (
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sitemaps",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_ckeditor_5",
    "widget_tweaks",
    "rest_framework",
    "rest_framework.authtoken",
    # JWT authentication
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "rules.apps.AutodiscoverRulesConfig",
    "easy_thumbnails",
    "parler",
    # Wagtail cms components
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.styleguide",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    "apps.cms.pages",
    "apps.cms.settings",
    "apps.cms.contacts",
    "apps.cms.news",
    "apps.cms.use_cases",
    "apps.cms.images",
    # General adhocracy 4 components
    "adhocracy4.actions",
    "adhocracy4.administrative_districts",
    "adhocracy4.categories",
    "adhocracy4.ckeditor",
    "adhocracy4.comments",
    "adhocracy4.comments_async",
    "adhocracy4.dashboard",
    "adhocracy4.exports",
    "adhocracy4.filters",
    "adhocracy4.follows",
    "adhocracy4.forms",
    "adhocracy4.images",
    "adhocracy4.labels",
    "adhocracy4.maps",
    "adhocracy4.modules",
    "adhocracy4.organisations",
    "adhocracy4.phases",
    "adhocracy4.polls",
    "adhocracy4.projects",
    "adhocracy4.ratings",
    "adhocracy4.reports",
    "adhocracy4.rules",
    # General components that define models or helpers
    "apps.actions",
    "apps.captcha",
    "apps.contrib",
    "apps.interactiveevents",
    "apps.maps",
    "apps.moderatorfeedback",
    "apps.moderatorremark",
    "apps.newsletters",
    "apps.notifications",
    "apps.organisations",
    "apps.users",
    # General apps containing views
    "apps.account",
    "apps.dashboard",
    "apps.exports",
    "apps.offlineevents",
    "apps.projects",
    "apps.userdashboard",
    # Apps defining phases
    "apps.activities",
    "apps.budgeting",
    "apps.documents",
    "apps.ideas",
    "apps.mapideas",
    "apps.polls",
    "apps.topicprio",
    "apps.debate",
)

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "django_cloudflare_push.middleware.push_middleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "apps.users.middleware.SetUserLanguageCookieMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "allauth.account.middleware.AccountMiddleware",
)

ROOT_URLCONF = "adhocracy-plus.config.urls"

LOCALE_PATHS = [
    # use the first line in branches and forks to keep the original translations
    # from main branch and overwrite or add extra translations in fork
    # os.path.join(BASE_DIR, 'locale-fork/locale'),
    os.path.join(BASE_DIR, "locale-source/locale")
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
            ],
        },
    },
]

WSGI_APPLICATION = "adhocracy-plus.config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        "TEST": {
            "NAME": os.path.join(BASE_DIR, "test_db.sqlite3"),
        },
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = "en"
DEFAULT_USER_LANGUAGE_CODE = "de"

TIME_ZONE = "Europe/Berlin"

USE_I18N = True


USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("de", _("German")),
    ("nl", _("Dutch")),
    ("ky", _("Kyrgyz")),
    ("ru", _("Russian")),
]

# adding language info for ky
EXTRA_LANG_INFO = {
    "ky": {
        "bidi": False,
        "code": "ky",
        "name": "Kyrgyz",
        "name_local": "Кыргызча",
    },
}
LANG_INFO = dict(locale.LANG_INFO, **EXTRA_LANG_INFO)
locale.LANG_INFO = LANG_INFO

PARLER_LANGUAGES = {
    1: [{"code": language_code} for language_code, language in LANGUAGES],
    "default": {
        "fallbacks": ["en", "de"],
    },
}

PARLER_ENABLE_CACHING = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, "static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

IMAGE_ALIASES = {
    "*": {
        "max_size": 5 * 10**6,
        "fileformats": ("image/png", "image/jpeg", "image/gif"),
    },
    "heroimage": {"min_resolution": (1500, 500)},
    "tileimage": {"min_resolution": (500, 300)},
    "logo": {
        "min_resolution": (200, 200),
        "max_resolution": (800, 800),
        "aspect_ratio": (1, 1),
    },
    "avatar": {"min_resolution": (200, 200)},
    "idea_image": {"min_resolution": (600, 400)},
    "eventimage": {"min_resolution": (500, 600)},
}

THUMBNAIL_ALIASES = {
    "": {
        "heroimage": {"size": (1500, 500), "crop": "smart"},
        "heroimage_preview": {"size": (880, 220), "crop": "smart"},
        "project_thumbnail": {"size": (520, 330), "crop": "smart"},
        "idea_image": {"size": (800, 0), "crop": "scale"},
        "idea_thumbnail": {"size": (240, 240), "crop": "smart"},
        "avatar": {"size": (200, 200), "crop": "smart"},
        "item_image": {"size": (330, 0), "crop": "scale"},
        "map_thumbnail": {"size": (200, 200), "crop": "smart"},
    }
}

ALLOWED_UPLOAD_IMAGES = ("png", "jpeg", "gif")


# Authentication

AUTH_USER_MODEL = "a4_candy_users.User"

AUTHENTICATION_BACKENDS = (
    "rules.permissions.ObjectPermissionBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_ADAPTER = "apps.users.adapters.AccountAdapter"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_FORMS = {
    "signup": "apps.users.forms.DefaultSignupForm",
    "login": "apps.users.forms.DefaultLoginForm",
}
ACCOUNT_RATE_LIMITS = {"login_failed": "10/5m/ip"}
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_USERNAME_MIN_LENGTH = 5
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_PREVENT_ENUMERATION = "strict"
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_FORMS = {"signup": "apps.users.forms.SocialTermsSignupForm"}
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

BLEACH_LIST = {
    "default": {
        "tags": [
            "a",
            "div",
            "em",
            "i",
            "iframe",
            "img",
            "li",
            "ol",
            "p",
            "strong",
            "u",
            "ul",
        ],
        "attributes": {
            "a": ["href", "rel", "target"],
            "img": ["src", "alt", "style"],
            "div": ["class"],
            "iframe": ["src", "alt", "style"],
        },
    },
    "image-editor": {
        "tags": [
            "a",
            "em",
            "figcaption",
            "figure",
            "i",
            "img",
            "li",
            "ol",
            "p",
            "span",
            "strong",
            "u",
            "ul",
        ],
        "attributes": {
            "a": ["href", "rel", "target"],
            "figure": ["class", "style"],
            "figcaption": ["class"],
            "img": ["class", "src", "alt", "style", "height", "width"],
            "span": ["class", "style"],
        },
        "styles": [
            "aspect-ratio",
            "float",
            "height",
            "margin",
            "margin-bottom",
            "margin-left",
            "margin-right",
            "margin-top",
            "padding",
            "width",
        ],
    },
    "collapsible-image-editor": {
        "tags": [
            "a",
            "div",
            "em",
            "figcaption",
            "figure",
            "i",
            "iframe",
            "img",
            "li",
            "ol",
            "p",
            "span",
            "strong",
            "u",
            "ul",
        ],
        "attributes": {
            "a": ["href", "rel", "target"],
            "div": ["class", "data-oembed-url"],
            "figure": ["class", "style"],
            "figcaption": ["class"],
            "iframe": ["src", "alt"],
            "img": ["class", "src", "alt", "style", "height", "width"],
            "span": ["class", "style"],
        },
        "styles": [
            "aspect-ratio",
            "float",
            "height",
            "margin",
            "margin-bottom",
            "margin-left",
            "margin-right",
            "margin-top",
            "padding",
            "width",
        ],
    },
    "video-editor": {
        "tags": ["a", "img", "div", "iframe", "figure"],
        "attributes": {
            "a": ["href", "rel", "target"],
            "img": ["src", "alt", "style"],
            "div": ["class", "data-oembed-url"],
            "iframe": ["src", "alt"],
            "figure": ["class", "div", "iframe"],
        },
    },
}

# Wagtail
WAGTAIL_SITE_NAME = "adhocracy+"
WAGTAILIMAGES_IMAGE_MODEL = "a4_candy_cms_images.CustomImage"

# adhocracy4

A4_ORGANISATIONS_MODEL = "a4_candy_organisations.Organisation"

# Set to False to disable the option to allow unregistered users in polls
A4_POLL_ENABLE_UNREGISTERED_USERS = True

A4_RATEABLES = (
    ("a4comments", "comment"),
    ("a4_candy_ideas", "idea"),
    ("a4_candy_mapideas", "mapidea"),
    ("a4_candy_budgeting", "proposal"),
    ("a4_candy_topicprio", "topic"),
)

A4_COMMENTABLES = (
    ("a4comments", "comment"),
    ("a4polls", "poll"),
    ("a4_candy_ideas", "idea"),
    ("a4_candy_documents", "chapter"),
    ("a4_candy_documents", "paragraph"),
    ("a4_candy_mapideas", "mapidea"),
    ("a4_candy_budgeting", "proposal"),
    ("a4_candy_topicprio", "topic"),
    ("a4_candy_debate", "subject"),
)

A4_COMMENT_CATEGORIES = (
    ("sug", _("suggestion")),
    ("not", _("note")),
    ("que", _("question")),
)

A4_REPORTABLES = (
    ("a4comments", "comment"),
    ("a4_candy_ideas", "idea"),
    ("a4_candy_mapideas", "mapidea"),
    ("a4_candy_budgeting", "proposal"),
)

A4_ACTIONABLES = (
    ("a4comments", "comment"),
    ("a4_candy_ideas", "idea"),
    ("a4_candy_budgeting", "proposal"),
    ("a4_candy_mapideas", "mapidea"),
    ("a4_candy_moderatorfeedback", "moderatorcommentfeedback"),
)

A4_AUTO_FOLLOWABLES = (
    ("a4comments", "comment"),
    ("a4polls", "vote"),
    ("a4_candy_ideas", "idea"),
    ("a4_candy_mapideas", "mapidea"),
    ("a4_candy_budgeting", "proposal"),
)

A4_CATEGORIZABLE = (
    ("a4_candy_ideas", "idea"),
    ("a4_candy_mapideas", "mapidea"),
    ("a4_candy_budgeting", "proposal"),
    ("a4_candy_topicprio", "topic"),
)

A4_LABELS_ADDABLE = (
    ("a4_candy_ideas", "idea"),
    ("a4_candy_mapideas", "mapidea"),
    ("a4_candy_budgeting", "proposal"),
    ("a4_candy_topicprio", "topic"),
)

A4_CATEGORY_ICONS = (
    ("", _("Pin without icon")),
    ("diamant", _("Diamond")),
    ("dreieck_oben", _("Triangle up")),
    ("dreieck_unten", _("Triangle down")),
    ("ellipse", _("Ellipse")),
    ("halbkreis", _("Semi circle")),
    ("hexagon", _("Hexagon")),
    ("parallelogramm", _("Rhomboid")),
    ("pentagramm", _("Star")),
    ("quadrat", _("Square")),
    ("raute", _("Octothorpe")),
    ("rechtecke", _("Rectangle")),
    ("ring", _("Circle")),
    ("rw_dreieck", _("Right triangle")),
    ("zickzack", _("Zigzag")),
)

A4_BLUEPRINT_TYPES = [
    ("BS", _("brainstorming")),
    ("MBS", _("spatial brainstorming")),
    ("IC", _("idea challenge")),
    ("MIC", _("spatial idea challenge")),
    ("TR", _("text review")),
    ("PO", _("poll")),
    ("PB", _("participatory budgeting")),
    ("IE", _("interactive event")),
    ("TP", _("prioritization")),
    ("DB", _("debate")),
]

A4_MAP_BASEURL = "https://{s}.tile.openstreetmap.org/"
A4_MAP_ATTRIBUTION = (
    '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
)
A4_MAP_BOUNDING_BOX = [[54.983, 15.016], [47.302, 5.988]]

A4_DASHBOARD = {
    "PROJECT_DASHBOARD_CLASS": "apps.dashboard.ProjectDashboard",
    "BLUEPRINTS": "apps.dashboard.blueprints.blueprints",
}

A4_ACTIONS_PHASE_ENDS_HOURS = 48

A4_USE_ORGANISATION_TERMS_OF_USE = True

# Disable CSP by default
CSP_REPORT_ONLY = True
CSP_DEFAULT_SRC = ["'self'", "'unsafe-inline'", "'unsafe-eval'", "data:", "blob:", "*"]

SITE_ID = 1  # overwrite this in local.py if needed

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Add a Captcheck captcha URL in the production server's local.py to use it
# Captcha software we use: https://source.netsyms.com/Netsyms/Captcheck
CAPTCHA_URL = ""

# Add insights for project if insight model exists
INSIGHT_MODEL = "a4_candy_projects.ProjectInsight"

# Celery configuration
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_RESULT_EXTENDED = True

# CKEditor5 config
CKEDITOR_5_FILE_STORAGE = "adhocracy4.ckeditor.storage.CustomStorage"
CKEDITOR_5_PATH_FROM_USERNAME = True
CKEDITOR_5_UNRESTRICTED_UPLOADS = True
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True
CKEDITOR_5_UPLOAD_FILE_TYPES = ["jpg", "jpeg", "png", "gif", "pdf", "docx"]
CKEDITOR_5_USER_LANGUAGE = True
CKEDITOR_5_CONFIGS = {
    "default": {
        "language": ["de", "en", "nl", "ru"],
        "toolbar": [
            "bold",
            "italic",
            "underline",
            "|",
            "link",
            "bulletedList",
            "numberedList",
        ],
        "list": {
            "properties": {
                "styles": "true",
                "startIndex": "true",
                "reversed": "true",
            }
        },
        "link": {"defaultProtocol": "https://"},
    },
    "image-editor": {
        "toolbar": {
            "items": [
                "bold",
                "italic",
                "underline",
                "bulletedList",
                "numberedList",
                "link",
                "imageUpload",
                "fileUpload",
            ],
            "shouldNotGroupWhenFull": "true",
        },
        "image": {
            "toolbar": [
                "imageUpload",
                "imageTextAlternative",
                "toggleImageCaption",
                "imageStyle:inline",
                "imageStyle:wrapText",
                "imageStyle:breakText",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
            ],
            "insert": {"type": "auto"},
        },
        "list": {
            "properties": {
                "styles": "true",
                "startIndex": "true",
                "reversed": "true",
            }
        },
        "link": {"defaultProtocol": "https://"},
    },
    "collapsible-image-editor": {
        "toolbar": [
            "bold",
            "italic",
            "underline",
            "bulletedList",
            "numberedList",
            "link",
            "imageUpload",
            "fileUpload",
            "mediaEmbed",
            "accordionButton",
            "fontSize",
        ],
        "image": {
            "toolbar": [
                "imageUpload",
                "imageTextAlternative",
                "toggleImageCaption",
                "imageStyle:inline",
                "imageStyle:wrapText",
                "imageStyle:breakText",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
            ],
            "insert": {"type": "auto"},
        },
        "list": {
            "properties": {
                "styles": "true",
                "startIndex": "true",
                "reversed": "true",
            }
        },
        "link": {"defaultProtocol": "https://"},
        "mediaEmbed": {
            "removeProviders": [
                "dailymotion",
                "spotify",
                "facebook",
                "flickr",
                "googleMaps",
                "instagram",
                "twitter",
            ],
            "previewsInData": True,
        },
    },
    "video-editor": {
        "toolbar": ["mediaEmbed"],
        "mediaEmbed": {
            "removeProviders": [
                "dailymotion",
                "spotify",
                "facebook",
                "flickr",
                "googleMaps",
                "instagram",
                "twitter",
            ],
            "previewsInData": True,
        },
    },
}
