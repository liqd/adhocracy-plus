from .dev import *

A4_ORGANISATION_FACTORY = 'tests.factories.OrganisationFactory'
A4_USER_FACTORY = 'tests.factories.UserFactory'

ACCOUNT_EMAIL_VERIFICATION = 'optional'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'postgres',
        'NAME': 'django',
        'TEST': {
            'NAME': 'django_test'
        },
    }
}
