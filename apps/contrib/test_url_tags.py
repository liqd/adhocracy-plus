import pytest

from adhocracy4.test import helpers


@pytest.mark.django_db
def test_get_absolute_uri(rf):
    request = rf.get('/')
    template = ('{% load absolute_url %}'
                '{% get_absolute_uri obj="/" as absolute_url %}'
                '{{ absolute_url }}')
    context = {'request': request}
    helpers.render_template(template, context)

    assert 'http://testserver/' == context['absolute_url']
    assert request.build_absolute_uri() == context['absolute_url']


@pytest.mark.django_db
def test_get_absolute_uri_static(rf):
    request = rf.get('/')
    template = ('{% load absolute_url %}'
                '{% get_absolute_uri_static obj="images/logo_01.png" '
                'as absolute_url %}'
                '{{ absolute_url }}')
    context = {'request': request}
    helpers.render_template(template, context)

    assert ('http://testserver/static/images/logo_01.png' ==
            context['absolute_url'])
