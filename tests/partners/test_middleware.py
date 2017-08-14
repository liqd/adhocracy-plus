import pytest
from django.http import Http404

from liqd_product.apps.partners import get_partner
from liqd_product.apps.partners import partner_context
from liqd_product.apps.partners import set_partner
from liqd_product.apps.partners.middleware import PartnerMiddleware


@pytest.mark.django_db
def test_middleware_set_partner(rf, partner):
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
def test_middleware_clear_partner(rf, partner):
    request = rf.get('/login/')
    middleware = PartnerMiddleware()

    set_partner(partner)
    middleware.process_view(request, None, None, {})

    assert get_partner() is None


@pytest.mark.django_db
def test_middleware_partner_context(partner):
    assert get_partner() is None
    with partner_context(partner):
        assert get_partner() == partner
    assert get_partner() is None
