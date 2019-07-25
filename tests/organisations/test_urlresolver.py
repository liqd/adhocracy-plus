import pytest
from django.conf.urls import include
from django.conf.urls import url
from django.views.defaults import page_not_found

from apps.organisations import set_organisation
from apps.organisations.urlresolvers import organisation_patterns
from apps.organisations.urlresolvers import reverse

base_urlconf = [
    url(r'^static/', page_not_found, name='static-url'),
    url(r'^dynamic/(?P<pk>\d+)/', page_not_found, name='dynamic-url'),
]


@pytest.mark.django_db
def test_organisation_patterns(organisation_factory):
    organisation = organisation_factory(slug='automatic_organisation',
                                        auto_set_organisation=False)
    set_organisation(organisation)
    urlconf = (organisation_patterns(
        *base_urlconf
    ),)

    url_ = reverse('static-url', urlconf)
    assert url_ == '/automatic_organisation/static/'

    url_ = reverse('static-url', urlconf, kwargs=dict(
        organisation_slug='manual_organisation'))
    assert url_ == '/manual_organisation/static/'

    url_ = reverse('dynamic-url', urlconf, kwargs=dict(pk=1))
    assert url_ == '/automatic_organisation/dynamic/1/'

    url_ = reverse('dynamic-url', urlconf, kwargs=dict(
        organisation_slug='manual_organisation', pk=1))
    assert url_ == '/manual_organisation/dynamic/1/'

    url_ = reverse('dynamic-url', urlconf, args=(1,))
    assert url_ == '/automatic_organisation/dynamic/1/'


@pytest.mark.django_db
def test_organisation_patterns_instance_ns(organisation_factory):
    organisation = organisation_factory(slug='automatic_organisation',
                                        auto_set_organisation=False)
    set_organisation(organisation)
    urlconf = (organisation_patterns(
        url(r'^ns/', include((base_urlconf, 'instance-ns'),
                             namespace='instance-ns'))
    ),)

    url_ = reverse('instance-ns:static-url', urlconf)
    assert url_ == '/automatic_organisation/ns/static/'

    url_ = reverse('instance-ns:static-url', urlconf, kwargs=dict(
        organisation_slug='manual_organisation'))
    assert url_ == '/manual_organisation/ns/static/'

    url_ = reverse('instance-ns:dynamic-url', urlconf, kwargs=dict(pk=1))
    assert url_ == '/automatic_organisation/ns/dynamic/1/'

    url_ = reverse('instance-ns:dynamic-url', urlconf, kwargs=dict(
        organisation_slug='manual_organisation', pk=1))
    assert url_ == '/manual_organisation/ns/dynamic/1/'

    url_ = reverse('instance-ns:dynamic-url', urlconf, args=(1,))
    assert url_ == '/automatic_organisation/ns/dynamic/1/'
