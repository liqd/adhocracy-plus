import pytest
from django.urls import reverse

from adhocracy4.projects import models
from adhocracy4.test.helpers import redirect_target


@pytest.mark.django_db
def test_anonymous_cannot_delete(client, project_factory):
    project = project_factory()
    count = models.Project.objects.all().count()
    assert count == 1
    url = reverse(
        'project-delete',
        kwargs={
            'organisation_slug': project.organisation.slug,
            'pk': project.pk
        })
    response = client.post(url)
    assert response.status_code == 302
    assert redirect_target(response) == 'account_login'
    count = models.Project.objects.all().count()
    assert count == 1


@pytest.mark.django_db
def test_user_cannot_delete(client, project_factory, user):
    project = project_factory()
    count = models.Project.objects.all().count()
    assert count == 1
    client.login(username=user.email, password='password')
    url = reverse(
        'project-delete',
        kwargs={
            'organisation_slug': project.organisation.slug,
            'pk': project.pk
        })
    response = client.post(url)
    assert response.status_code == 403
    count = models.Project.objects.all().count()
    assert count == 1


@pytest.mark.django_db
def test_moderator_cannot_delete(client, project_factory, user):
    project = project_factory()
    count = models.Project.objects.all().count()
    assert count == 1
    moderator = project.moderators.first()
    client.login(username=moderator.email, password='password')
    url = reverse(
        'project-delete',
        kwargs={
            'organisation_slug': project.organisation.slug,
            'pk': project.pk
        })
    response = client.post(url)
    assert response.status_code == 403
    count = models.Project.objects.all().count()
    assert count == 1


@pytest.mark.django_db
def test_initator_can_delete(client, project_factory):
    project = project_factory()
    count = models.Project.objects.all().count()
    assert count == 1
    initiator = project.organisation.initiators.first()
    client.login(username=initiator.email, password='password')
    url = reverse(
        'project-delete',
        kwargs={
            'organisation_slug': project.organisation.slug,
            'pk': project.pk
        })
    response = client.get(url)
    assert response.status_code == 405
    response = client.post(url)
    assert response.status_code == 302
    count = models.Project.objects.all().count()
    assert count == 0
