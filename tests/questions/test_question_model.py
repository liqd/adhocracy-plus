import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_absolute_url(question):
    url = reverse('module-detail',
                  kwargs={'organisation_slug':
                          question.module.project.organisation.slug,
                          'module_slug': question.module.slug})
    assert question.get_absolute_url() == url


@pytest.mark.django_db
def test_str(question):
    question_string = str(question)
    assert question_string == question.text


@pytest.mark.django_db
def test_creator_is_anonymous(question):
    creator = question.creator
    assert creator.__class__.__name__ == 'AnonymousUser'
    assert str(creator) == 'AnonymousUser'


@pytest.mark.django_db
def test_project(question):
    assert question.module.project == question.project
