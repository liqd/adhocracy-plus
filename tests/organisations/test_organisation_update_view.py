import pytest
from django.urls import reverse

from adhocracy4.test.helpers import redirect_target
from apps.organisations import models


@pytest.mark.django_db
def test_initiator_can_update(client, organisation):
    initiator = organisation.initiators.first()
    client.login(username=initiator, password='password')
    url = reverse('organisation-settings',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 200
    data = {
        'title': 'Organisation platform title',
        'description': 'some very short description of the organisation',
        'imprint': 'Organisation imprint'
    }
    response = client.post(url, data)
    assert redirect_target(response) == 'organisation-settings'
    assert response.status_code == 302
    updated_organisation = models.Organisation.objects.get(id=organisation.id)
    assert updated_organisation.title == 'Organisation platform title'
    assert updated_organisation.description == \
        'some very short description of the organisation'


@pytest.mark.django_db
def test_user_cannot_update(client, organisation, user):
    client.login(username=user, password='password')
    url = reverse('organisation-settings',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 403
    data = {
        'title': 'Organisation platform title',
        'description': 'some very short description of the organisation',
        'imprint': 'Organisation imprint'
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderator_cannot_update(client, project):
    organisation = project.organisation
    moderator = project.moderators.first()
    client.login(username=moderator, password='password')
    url = reverse('organisation-settings',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 403
    data = {
        'title': 'Organisation platform title',
        'description': 'some very short description of the organisation',
        'imprint': 'Organisation imprint'
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_member_cannot_update(client, member):
    organisation = member.organisation
    client.login(username=member.member, password='password')
    url = reverse('organisation-settings',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 403
    data = {
        'title': 'Organisation platform title',
        'description': 'some very short description of the organisation',
        'imprint': 'Organisation imprint'
    }
    response = client.post(url, data)
    assert response.status_code == 403
