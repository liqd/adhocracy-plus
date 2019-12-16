import pytest
from django.urls import reverse

from adhocracy4.comments import models as comments_models
from apps.debate.models import Subject


@pytest.mark.django_db
def test_absolute_url(subject):
    url = reverse(
        'a4_candy_debate:subject-detail',
        kwargs={
            'organisation_slug': subject.module.project.organisation.slug,
            'pk': '{:05d}'.format(subject.pk),
            'year': subject.created.year
        })
    assert subject.get_absolute_url() == url


@pytest.mark.django_db
def test_str(subject):
    subject_string = subject.__str__()
    assert subject_string == subject.name


@pytest.mark.django_db
def test_project(subject):
    assert subject.module.project == subject.project


@pytest.mark.django_db
def test_delete_subject(subject_factory, comment_factory, rating_factory):
    subject = subject_factory()

    for i in range(5):
        comment_factory(content_object=subject)
    comment_count = comments_models.Comment.objects.all().count()
    assert comment_count == len(subject.comments.all())

    count = Subject.objects.all().count()
    assert count == 1
    assert comment_count == 5

    subject.delete()
    count = Subject.objects.all().count()
    comment_count = comments_models.Comment.objects.all().count()
    assert count == 0
    assert comment_count == 0
