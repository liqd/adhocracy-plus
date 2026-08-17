import os

from .test import *

# E2E tests run against a self-contained SQLite (spatialite) database so that
# the pytest-django live server, the Playwright browser and the seeding
# fixtures all share the same file without depending on a local/CI Postgres
# set-up. spatialite is available in the CI base image.
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.spatialite",
        "NAME": os.path.join(BASE_DIR, "test_db.sqlite3"),
        "TEST": {
            "NAME": os.path.join(BASE_DIR, "test_db_e2e.sqlite3"),
        },
    }
}
