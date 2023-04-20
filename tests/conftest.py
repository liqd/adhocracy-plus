from io import BytesIO

import factory
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.urls.base import get_resolver
from PIL import Image
from pytest_factoryboy import register
from rest_framework.test import APIClient

from adhocracy4.test import factories as a4_factories
from adhocracy4.test.factories.maps import AreaSettingsFactory
from adhocracy4.test.helpers import patch_background_task_decorator

from . import factories


def pytest_configure(config):
    # Patch email background_task decorators for all tests
    patch_background_task_decorator("adhocracy4.emails.tasks")
    patch_background_task_decorator("apps.projects.tasks")

    # Populate reverse dict with organisation patterns
    resolver = get_resolver()
    resolver.reverse_dict


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


@pytest.fixture
def apiclient():
    return APIClient()


@pytest.fixture
def ImagePNG():
    return factory.django.ImageField(width=1500, height=1400, format="PNG")


@pytest.fixture
def ImageBMP():
    return factory.django.ImageField(width=1500, height=1400, format="BMP")


@pytest.fixture
def smallImage():
    return factory.django.ImageField(width=200, height=200)


@pytest.fixture
def bigImage():
    return factory.django.ImageField(width=1500, height=1400)


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
