import pytest
from django.urls import reverse

from adhocracy4.test.helpers import redirect_target


@pytest.mark.django_db
def test_user_cannot_update(client, subject_factory):
    subject = subject_factory()
    user = subject.creator
    assert user not in subject.module.project.moderators.all()
    url = reverse(
        'a4dashboard:subject-update',
        kwargs={
            'organisation_slug': subject.module.project.organisation.slug,
            'pk': subject.pk,
            'year': subject.created.year
        })
    client.login(username=user.email, password='password')
    data = {
        'name': 'Another Subject'
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderators_can_always_update(client, subject_factory):
    subject = subject_factory()
    moderator = subject.module.project.moderators.first()
    assert moderator is not subject.creator
    url = reverse(
        'a4dashboard:subject-update',
        kwargs={
            'organisation_slug': subject.module.project.organisation.slug,
            'pk': subject.pk,
            'year': subject.created.year
        })
    client.login(username=moderator.email, password='password')
    data = {
        'name': 'Another subject'
    }
    response = client.post(url, data)
    assert redirect_target(response) == 'subject-list'
    assert response.status_code == 302
