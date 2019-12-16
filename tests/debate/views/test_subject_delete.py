import pytest
from django.urls import reverse

from adhocracy4.test.helpers import redirect_target
from apps.debate import models


@pytest.mark.django_db
def test_anonymous_cannot_delete(client, subject_factory):
    subject = subject_factory()
    url = reverse(
        'a4dashboard:subject-delete',
        kwargs={
            'organisation_slug': subject.module.project.organisation.slug,
            'pk': subject.pk,
            'year': subject.created.year
        })
    response = client.post(url)
    assert response.status_code == 302
    assert redirect_target(response) == 'account_login'


@pytest.mark.django_db
def test_user_cannot_delete(client, subject_factory, user):
    subject = subject_factory()
    client.login(username=user.email, password='password')
    url = reverse(
        'a4dashboard:subject-delete',
        kwargs={
            'organisation_slug': subject.module.project.organisation.slug,
            'pk': subject.pk,
            'year': subject.created.year
        })
    response = client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderator_can_delete(client, subject_factory):
    subject = subject_factory()
    moderator = subject.module.project.moderators.first()
    client.login(username=moderator.email, password='password')
    url = reverse(
        'a4dashboard:subject-delete',
        kwargs={
            'organisation_slug': subject.module.project.organisation.slug,
            'pk': subject.pk,
            'year': subject.created.year
        })
    response = client.post(url)
    assert response.status_code == 302
    assert redirect_target(response) == 'subject-list'
    count = models.Subject.objects.all().count()
    assert count == 0


@pytest.mark.django_db
def test_initator_can_delete(client, subject_factory):
    subject = subject_factory()
    initiator = subject.module.project.organisation.initiators.first()
    client.login(username=initiator.email, password='password')
    url = reverse(
        'a4dashboard:subject-delete',
        kwargs={
            'organisation_slug': subject.module.project.organisation.slug,
            'pk': subject.pk,
            'year': subject.created.year
        })
    response = client.post(url)
    assert response.status_code == 302
    assert redirect_target(response) == 'subject-list'
    count = models.Subject.objects.all().count()
    assert count == 0


@pytest.mark.django_db
def test_admin_can_delete(client, subject_factory, admin):
    subject = subject_factory()
    client.login(username=admin.email, password='password')
    url = reverse(
        'a4dashboard:subject-delete',
        kwargs={
            'organisation_slug': subject.module.project.organisation.slug,
            'pk': subject.pk,
            'year': subject.created.year
        })
    response = client.post(url)
    assert response.status_code == 302
    assert redirect_target(response) == 'subject-list'
    count = models.Subject.objects.all().count()
    assert count == 0
