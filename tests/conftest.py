import uuid
from io import BytesIO

import factory
import pytest
from celery import Celery
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from pytest_factoryboy import register
from rest_framework.test import APIClient

from adhocracy4.test import factories as a4_factories
from adhocracy4.test.factories.maps import AreaSettingsFactory

from . import factories

register(factories.UserFactory)
register(factories.UserFactory, "user2")
register(factories.AdminFactory, "admin")
register(factories.OrganisationFactory)
register(factories.MemberFactory)
register(factories.OrganisationTermsOfUseFactory)

register(a4_factories.PhaseFactory)
register(a4_factories.PhaseContentFactory)
register(factories.CategoryFactory)
register(factories.LabelFactory)
register(factories.CommentFactory)
register(factories.RatingFactory)
register(factories.ModeratorFeedbackFactory)
register(factories.ReportFactory)

register(a4_factories.GroupFactory)
register(a4_factories.ProjectFactory)
register(a4_factories.ModuleFactory)
register(AreaSettingsFactory)


def pytest_configure():
    Celery(task_always_eager=True)


def pytest_collection_modifyitems(config, items):
    # Do not run browser e2e tests by default. Run them explicitly with
    # `py.test -m e2e` (which sets config.option.markexpr).
    if config.option.markexpr:
        return
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(pytest.mark.skip(reason="e2e: run with `py.test -m e2e`"))


@pytest.fixture
def apiclient():
    return APIClient()


@pytest.fixture
def image_png():
    return factory.django.ImageField(
        width=1500,
        height=1400,
        format="PNG",
        filename=f"example-{uuid.uuid4().hex}.png",
    )


@pytest.fixture
def image_webp():
    return factory.django.ImageField(
        width=1500,
        height=1400,
        format="WEBP",
        filename=f"example-{uuid.uuid4().hex}.webp",
    )


@pytest.fixture
def image_bmp():
    return factory.django.ImageField(
        width=1500,
        height=1400,
        format="BMP",
        filename=f"example-{uuid.uuid4().hex}.bmp",
    )


@pytest.fixture
def small_image():
    return factory.django.ImageField(
        width=200, height=200, filename=f"example-{uuid.uuid4().hex}.jpg"
    )


@pytest.fixture
def big_image():
    return factory.django.ImageField(
        width=1500, height=1400, filename=f"example-{uuid.uuid4().hex}.jpg"
    )


@pytest.fixture
def test_file():
    return factory.django.FileField(data=b"examplefile")


@pytest.fixture
def login_url():
    return reverse("account_login")


@pytest.fixture
def logout_url():
    return reverse("account_logout")


@pytest.fixture
def signup_url():
    return reverse("account_signup")


@pytest.fixture()
def image_factory():
    def _get_image_data(width=1500, height=1500):
        image = BytesIO()
        Image.new("RGB", (width, height)).save(image, "JPEG")
        return SimpleUploadedFile("image.JPG", image.getvalue())

    return _get_image_data


@pytest.fixture
def geos_point():
    return Point(13.397788148643649, 52.52958586909979)


def get_geojson_point():
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [13.397788148643649, 52.52958586909979],
        },
    }


@pytest.fixture
def geojson_point():
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [13.397788148643649, 52.52958586909979],
        },
        "properties": {"strname": None, "hsnr": None, "plz": None},
    }


@pytest.fixture
def geojson_point_str():
    return '{"type": "Feature","geometry": {"type": "Point", "coordinates": [13.397788148643649, 52.52958586909979]}}'
