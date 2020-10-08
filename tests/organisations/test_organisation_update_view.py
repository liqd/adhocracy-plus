import pytest
from django.urls import reverse
from parler.utils.context import switch_language

from adhocracy4.test.helpers import redirect_target
from apps.organisations import models


@pytest.mark.django_db
def test_initiator_can_update(client, organisation):
    initiator = organisation.initiators.first()
    client.login(username=initiator, password='password')
    url = reverse('a4dashboard:organisation-settings',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 200
    data = {
        'title': 'Organisation platform title',
        'language': 'de',
        'en': 'en',
        'en__description': 'some very short description of the organisation',
        'en__slogan': 'some slogan in English',
        'en__information': 'This is very important info!',
        'de': 'de',
        'de__description': 'Eine sehr kurze Beschreibung der Organisation',
        'de__slogan': 'Slogan auf Deutsch',
        'de__information': 'Ein paar wichtige Informationen',
    }
    response = client.post(url, data)
    assert redirect_target(response) == 'organisation-settings'
    assert response.status_code == 302
    organisation.refresh_from_db()
    organisation.get_translation('en').refresh_from_db()
    assert organisation.title == 'Organisation platform title'
    assert organisation.language == 'de'
    assert organisation.description == \
        'some very short description of the organisation'
    assert organisation.slogan == 'some slogan in English'
    assert organisation.information == 'This is very important info!'

    with switch_language(organisation, 'de'):
        assert organisation.description == \
            'Eine sehr kurze Beschreibung der Organisation'
        assert organisation.slogan == 'Slogan auf Deutsch'
        assert organisation.information == 'Ein paar wichtige Informationen'


@pytest.mark.django_db
def test_initiator_can_delete_language(client, organisation):
    initiator = organisation.initiators.first()
    client.login(username=initiator, password='password')
    url = reverse('a4dashboard:organisation-settings',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 200

    with switch_language(organisation, 'de'):
        organisation.description = 'desc.de'
        organisation.description_why = 'desc why.de'
        organisation.description_how = 'desc how.de'
        organisation.save()

    data = {
        'title': 'Organisation platform title',
        'language': 'de',
        'en': 'en',
        'en__description': 'some very short description of the organisation',
        'en__slogan': 'some slogan in English',
        'en__information': 'This is very important info!',
        'de__description': 'Eine sehr kurze Beschreibung der Organisation',
        'de__slogan': 'Slogan auf Deutsch',
        'de__information': 'Ein paar wichtige Informationen',
    }
    response = client.post(url, data)
    assert redirect_target(response) == 'organisation-settings'
    assert response.status_code == 302
    organisation.refresh_from_db()
    organisation.get_translation('en').refresh_from_db()
    assert organisation.description == \
        'some very short description of the organisation'
    assert organisation.slogan == 'some slogan in English'
    assert organisation.information == 'This is very important info!'

    with switch_language(organisation, 'de'):
        assert organisation.description == \
            'some very short description of the organisation'
        assert organisation.slogan == 'some slogan in English'
        assert organisation.information == 'This is very important info!'


@pytest.mark.django_db
def test_initiator_can_update_legal_info(client, organisation):
    initiator = organisation.initiators.first()
    client.login(username=initiator, password='password')
    url = reverse('a4dashboard:organisation-legal-information',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 200
    data = {
        'imprint': 'Organisation imprint',
        'netiquette': 'Be nice with each other.'
    }
    response = client.post(url, data)
    assert redirect_target(response) == 'organisation-legal-information'
    assert response.status_code == 302
    updated_organisation = models.Organisation.objects.get(id=organisation.id)
    assert updated_organisation.imprint == 'Organisation imprint'
    assert updated_organisation.netiquette == 'Be nice with each other.'


@pytest.mark.django_db
def test_user_cannot_update(client, organisation, user):
    client.login(username=user, password='password')
    url = reverse('a4dashboard:organisation-settings',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 403
    data = {
        'title': 'Organisation platform title',
        'language': 'de',
        'en': 'en',
        'en__description': 'some very short description of the organisation',
        'en__slogan': 'some slogan in English',
        'en__information': 'This is very important info!',
        'de': 'de',
        'de__description': 'Eine sehr kurze Beschreibung der Organisation',
        'de__slogan': 'Slogan auf Deutsch',
        'de__information': 'Ein paar wichtige Informationen',
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_update_legal_info(client, organisation, user):
    client.login(username=user, password='password')
    url = reverse('a4dashboard:organisation-legal-information',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 403
    data = {
        'imprint': 'Organisation imprint',
        'netiquette': 'Be nice with each other.'
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderator_cannot_update(client, project):
    organisation = project.organisation
    moderator = project.moderators.first()
    client.login(username=moderator, password='password')
    url = reverse('a4dashboard:organisation-settings',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 403
    data = {
        'title': 'Organisation platform title',
        'language': 'de',
        'en': 'en',
        'en__description': 'some very short description of the organisation',
        'en__slogan': 'some slogan in English',
        'en__information': 'This is very important info!',
        'de': 'de',
        'de__description': 'Eine sehr kurze Beschreibung der Organisation',
        'de__slogan': 'Slogan auf Deutsch',
        'de__information': 'Ein paar wichtige Informationen',
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderator_cannot_update_legal_info(client, project):
    organisation = project.organisation
    moderator = project.moderators.first()
    client.login(username=moderator, password='password')
    url = reverse('a4dashboard:organisation-legal-information',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 403
    data = {
        'imprint': 'Organisation imprint',
        'netiquette': 'Be nice with each other.'
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_member_cannot_update(client, member):
    organisation = member.organisation
    client.login(username=member.member, password='password')
    url = reverse('a4dashboard:organisation-settings',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 403
    data = {
        'title': 'Organisation platform title',
        'language': 'de',
        'en': 'en',
        'en__description': 'some very short description of the organisation',
        'en__slogan': 'some slogan in English',
        'en__information': 'This is very important info!',
        'de': 'de',
        'de__description': 'Eine sehr kurze Beschreibung der Organisation',
        'de__slogan': 'Slogan auf Deutsch',
        'de__information': 'Ein paar wichtige Informationen',
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_member_cannot_update_legal_info(client, member):
    organisation = member.organisation
    client.login(username=member.member, password='password')
    url = reverse('a4dashboard:organisation-legal-information',
                  kwargs={'organisation_slug': organisation.slug})
    response = client.get(url)
    assert response.status_code == 403
    data = {
        'imprint': 'Organisation imprint',
        'netiquette': 'Be nice with each other.'
    }
    response = client.post(url, data)
    assert response.status_code == 403
