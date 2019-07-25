import pytest
from django.http import Http404

from apps.organisations import get_organisation
from apps.organisations import organisation_context
from apps.organisations import set_organisation
from apps.organisations.middleware import OrganisationMiddleware


@pytest.mark.django_db
def test_middleware_set_organisation(rf, organisation_factory):
    organisation = organisation_factory(auto_set_organisation=False)
    slug = organisation.slug
    request = rf.get('/%s/' % slug)
    middleware = OrganisationMiddleware()

    middleware.process_view(request, None, None, {
        'organisation_slug': slug
    })

    assert get_organisation() == organisation


@pytest.mark.django_db
def test_middleware_organisation_not_found(rf):
    request = rf.get('/unknown/')
    middleware = OrganisationMiddleware()

    with pytest.raises(Http404):
        middleware.process_view(request, None, None, {
            'organisation_slug': 'unknown'
        })


@pytest.mark.django_db
def test_middleware_clear_organisation(rf, organisation_factory):
    organisation = organisation_factory(auto_set_organisation=False)
    request = rf.get('/login/')
    middleware = OrganisationMiddleware()

    set_organisation(organisation)
    middleware.process_view(request, None, None, {})

    assert get_organisation() is None


@pytest.mark.django_db
def test_middleware_organisation_context(organisation_factory):
    organisation = organisation_factory(auto_set_organisation=False)
    assert get_organisation() is None
    with organisation_context(organisation):
        assert get_organisation() == organisation
    assert get_organisation() is None
