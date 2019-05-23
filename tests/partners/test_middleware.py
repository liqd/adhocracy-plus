import pytest
from django.http import Http404

from apps.partners import get_partner
from apps.partners import partner_context
from apps.partners import set_partner
from apps.partners.middleware import PartnerMiddleware


@pytest.mark.django_db
def test_middleware_set_partner(rf, partner_factory):
    partner = partner_factory(auto_set_partner=False)
    slug = partner.slug
    request = rf.get('/%s/' % slug)
    middleware = PartnerMiddleware()

    middleware.process_view(request, None, None, {
        'partner_slug': slug
    })

    assert get_partner() == partner


@pytest.mark.django_db
def test_middleware_partner_not_found(rf):
    request = rf.get('/unknown/')
    middleware = PartnerMiddleware()

    with pytest.raises(Http404):
        middleware.process_view(request, None, None, {
            'partner_slug': 'unknown'
        })


@pytest.mark.django_db
def test_middleware_clear_partner(rf, partner_factory):
    partner = partner_factory(auto_set_partner=False)
    request = rf.get('/login/')
    middleware = PartnerMiddleware()

    set_partner(partner)
    middleware.process_view(request, None, None, {})

    assert get_partner() is None


@pytest.mark.django_db
def test_middleware_partner_context(partner_factory):
    partner = partner_factory(auto_set_partner=False)
    assert get_partner() is None
    with partner_context(partner):
        assert get_partner() == partner
    assert get_partner() is None
