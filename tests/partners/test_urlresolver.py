import pytest
from django.conf.urls import include
from django.conf.urls import url
from django.views.defaults import page_not_found

from liqd_product.apps.partners import set_partner
from liqd_product.apps.partners.urlresolvers import partner_patterns
from liqd_product.apps.partners.urlresolvers import reverse

base_urlconf = [
    url(r'^static/', page_not_found, name='static-url'),
    url(r'^dynamic/(?P<pk>\d+)/', page_not_found, name='dynamic-url'),
]


@pytest.mark.django_db
def test_partner_patterns(partner_factory):
    partner = partner_factory(slug='automatic_partner',
                              auto_set_partner=False)
    set_partner(partner)
    urlconf = (partner_patterns(
        *base_urlconf
    ),)

    url_ = reverse('static-url', urlconf)
    assert url_ == '/automatic_partner/static/'

    url_ = reverse('static-url', urlconf, kwargs=dict(
        partner_slug='manual_partner'))
    assert url_ == '/manual_partner/static/'

    url_ = reverse('dynamic-url', urlconf, kwargs=dict(pk=1))
    assert url_ == '/automatic_partner/dynamic/1/'

    url_ = reverse('dynamic-url', urlconf, kwargs=dict(
        partner_slug='manual_partner', pk=1))
    assert url_ == '/manual_partner/dynamic/1/'

    url_ = reverse('dynamic-url', urlconf, args=(1,))
    assert url_ == '/automatic_partner/dynamic/1/'


@pytest.mark.django_db
def test_partner_patterns_instance_ns(partner_factory):
    partner = partner_factory(slug='automatic_partner',
                              auto_set_partner=False)
    set_partner(partner)
    urlconf = (partner_patterns(
        url(r'^ns/', include(base_urlconf, namespace='instance-ns'))
    ),)

    url_ = reverse('instance-ns:static-url', urlconf)
    assert url_ == '/automatic_partner/ns/static/'

    url_ = reverse('instance-ns:static-url', urlconf, kwargs=dict(
        partner_slug='manual_partner'))
    assert url_ == '/manual_partner/ns/static/'

    url_ = reverse('instance-ns:dynamic-url', urlconf, kwargs=dict(pk=1))
    assert url_ == '/automatic_partner/ns/dynamic/1/'

    url_ = reverse('instance-ns:dynamic-url', urlconf, kwargs=dict(
        partner_slug='manual_partner', pk=1))
    assert url_ == '/manual_partner/ns/dynamic/1/'

    url_ = reverse('instance-ns:dynamic-url', urlconf, args=(1,))
    assert url_ == '/automatic_partner/ns/dynamic/1/'
