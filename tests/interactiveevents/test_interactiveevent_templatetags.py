import pytest
from django.urls import reverse

from adhocracy4.test.helpers import render_template


@pytest.mark.django_db
def test_react_questions(rf, user, live_question):
    request = rf.get('/')
    request.user = user
    module = live_question.module
    template = '{% load react_interactiveevents %}' \
        '{% react_interactiveevents module %}'
    context = {'request': request, "module": module}

    questions_api_url = reverse('interactiveevents-list',
                                kwargs={'module_pk': module.pk})
    present_url = reverse('question-present',
                          kwargs={'module_slug': module.slug,
                                  'organisation_slug':
                                      module.project.organisation.slug})
    rendered = render_template(template, context)

    assert rendered.startswith('<div data-aplus-widget="questions"')
    assert module.description.replace('\n', '\\n') in rendered
    assert questions_api_url in rendered
    assert present_url in rendered
    assert live_question.category.name in rendered


@pytest.mark.django_db
def test_react_questions_present(rf, user, live_question):
    request = rf.get('/')
    request.user = user
    module = live_question.module
    template = '{% load react_interactiveevents %}' \
        '{% react_interactiveevents_present module %}'
    context = {'request': request, "module": module}

    questions_api_url = reverse('interactiveevents-list',
                                kwargs={'module_pk': module.pk})
    rendered = render_template(template, context)

    assert rendered.startswith('<div data-aplus-widget="present"')
    assert questions_api_url in rendered
    assert live_question.category.name in rendered
    assert module.project.name in rendered
