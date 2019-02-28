import pytest
from django.urls.base import get_resolver
from pytest_factoryboy import register
from rest_framework.test import APIClient

from adhocracy4.test import factories as a4_factories
from adhocracy4.test.factories.maps import AreaSettingsFactory
from adhocracy4.test.helpers import patch_background_task_decorator
from liqd_product.apps.django_overwrites.urlresolvers import patch_reverse

from . import factories
from .partners import factories as partner_factories


def pytest_configure(config):
    # Patch the reverse function.
    # This is required as modules are imported by pytest prior to app init
    patch_reverse()
    # Patch email background_task decorators for all tests
    patch_background_task_decorator('adhocracy4.emails.tasks')

    # Populate reverse dict with partner patterns
    resolver = get_resolver()
    resolver.reverse_dict


register(factories.UserFactory)
register(factories.UserFactory, 'user2')
register(factories.AdminFactory, 'admin')
register(factories.OrganisationFactory)
register(partner_factories.PartnerFactory)

register(factories.PhaseFactory)
register(factories.PhaseContentFactory)
register(factories.CategoryFactory)
register(factories.CommentFactory)
register(factories.ModeratorStatementFactory)

register(a4_factories.ProjectFactory)
register(a4_factories.ModuleFactory)
register(AreaSettingsFactory)


@pytest.fixture
def apiclient():
    return APIClient()
