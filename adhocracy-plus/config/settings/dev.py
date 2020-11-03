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

# DIID specific test saml2 config
from os import path

import saml2
import saml2.saml

BASEDIR = path.dirname(path.abspath(__file__))

SAML_CONFIG = {
  'entityid': 'http://app.example.com',
  'allow_unknown_attributes': True,
  'attribute_map_dir': path.join(BASEDIR, 'saml', 'attribute-maps'),
  'service': {
    'sp': {
      'name': 'Federated Django sample SP',
      'name_id_format': saml2.saml.NAMEID_FORMAT_PERSISTENT,
      'endpoints': {
        'single_logout_service': [
          ('http://localhost:8004/saml2/ls/', saml2.BINDING_HTTP_REDIRECT),
          ('http://localhost:8004/saml2/ls/post', saml2.BINDING_HTTP_POST),
        ],
        'assertion_consumer_service': [
          ('http://localhost:8004/saml2/acs/', saml2.BINDING_HTTP_POST),
        ],
      },
      'required_attributes': ['mail'],
    },
  },
  'metadata': {
    'remote': [{"url": "http://localhost:8080/simplesaml/saml2/idp/metadata.php"},],
  },
  'key_file': path.join(BASEDIR, 'saml', 'private.key'),
  'cert_file': path.join(BASEDIR, 'saml', 'cert.pem'),
  'encryption_keypairs': [{
    'key_file': path.join(BASEDIR, 'saml', 'private.key'),
    'cert_file': path.join(BASEDIR, 'saml', 'cert.pem'),
  }],
  'debug': 1,
}
SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email'
SAML_LOGOUT_REQUEST_PREFERRED_BINDING = saml2.BINDING_HTTP_REDIRECT
SAML_ATTRIBUTE_MAPPING = {
    'mail': ['email', 'set_username_from_email'],
}
