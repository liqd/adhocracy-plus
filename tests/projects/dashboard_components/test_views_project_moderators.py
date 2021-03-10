import os

import pytest
from django.contrib.messages import get_messages
from django.core import mail
from django.test import override_settings

from adhocracy4.dashboard import components
from adhocracy4.test.helpers import redirect_target
from apps.ideas.phases import CollectFeedbackPhase
from apps.projects.models import ModeratorInvite
from tests.helpers import assert_template_response
from tests.helpers import setup_phase

component = components.projects.get('moderators')


@override_settings(
    USE_I18N=True,
    LOCALE_PATHS=[
        os.path.join(os.path.dirname(__file__), 'locale'),
    ],
    LANGUAGE_CODE='de',
    LANGUAGES=[
        ('en', 'English'),
        ('de', 'German'),
        ('nl', 'Dutch'),
        ('ky', 'Kyrgyz'),
        ('ru', 'Russian'),
    ],
)
@pytest.mark.django_db
def test_initiator_can_edit(client, phase_factory):
    phase, module, project, idea = setup_phase(
        phase_factory, None, CollectFeedbackPhase)
    organisation = project.organisation
    organisation.language = 'de'
    organisation.save()
    url = component.get_base_url(project)
    initiator = module.project.organisation.initiators.first()
    client.login(username=initiator.email, password='password')
    response = client.get(url)
    assert_template_response(
        response, 'a4_candy_projects/project_moderators.html')

    data = {
        'add_users': 'test1@foo.bar,test2@foo.bar',
    }
    response = client.post(url, data)
    assert redirect_target(response) == \
        'dashboard-{}-edit'.format(component.identifier)
    assert ModeratorInvite.objects.get(email='test1@foo.bar')
    assert ModeratorInvite.objects.get(email='test2@foo.bar')
    assert len(mail.outbox) == 2
    assert mail.outbox[0].subject.startswith(
        'Einladung zum Moderieren des Projekts:')


@pytest.mark.django_db
def test_initiator_can_delete_invitation(client, phase_factory):
    phase, module, project, idea = setup_phase(
        phase_factory, None, CollectFeedbackPhase)
    url = component.get_base_url(project)
    initiator = module.project.organisation.initiators.first()
    client.login(username=initiator.email, password='password')
    response = client.get(url)
    assert_template_response(
        response, 'a4_candy_projects/project_moderators.html')

    data = {
        'add_users': 'test1@foo.bar,test2@foo.bar',
    }
    response = client.post(url, data)
    assert redirect_target(response) == \
        'dashboard-{}-edit'.format(component.identifier)
    assert ModeratorInvite.objects.get(email='test1@foo.bar')
    invite_pk = int(ModeratorInvite.objects.get(email='test1@foo.bar').pk)
    data = {
        'submit_action': 'remove_invite',
        'invite_pk': invite_pk

    }
    response = client.post(url, data)
    assert redirect_target(response) == \
        'dashboard-{}-edit'.format(component.identifier)
    assert response.status_code == 302
    assert not ModeratorInvite.objects.filter(email='test1@foo.bar').exists()
    response = client.post(url, data)
    assert redirect_target(response) == \
        'dashboard-{}-edit'.format(component.identifier)
    assert response.status_code == 302


@pytest.mark.django_db
def test_initiator_can_delete_moderator(client, phase_factory, user):
    phase, module, project, idea = setup_phase(
        phase_factory, None, CollectFeedbackPhase)
    assert user not in module.project.moderators.all()
    module.project.moderators.add(user)
    url = component.get_base_url(project)
    initiator = module.project.organisation.initiators.first()
    client.login(username=initiator.email, password='password')
    user_pk = user.pk
    data = {
        'submit_action': 'remove_user',
        'user_pk': user_pk

    }
    response = client.post(url, data)
    assert redirect_target(response) == \
        'dashboard-{}-edit'.format(component.identifier)
    assert response.status_code == 302
    assert user not in module.project.moderators.all()
    response = client.post(url, data)
    assert redirect_target(response) == \
        'dashboard-{}-edit'.format(component.identifier)
    assert response.status_code == 302


@pytest.mark.django_db
def test_moderator_can_only_be_invited_once(
        client, phase_factory, user):
    phase, module, project, idea = setup_phase(
        phase_factory, None, CollectFeedbackPhase)
    assert user not in module.project.moderators.all()
    module.project.moderators.add(user)
    url = component.get_base_url(project)
    initiator = module.project.organisation.initiators.first()
    client.login(username=initiator.email, password='password')
    response = client.get(url)
    assert_template_response(
        response, 'a4_candy_projects/project_moderators.html')

    data = {
        'add_users': 'test1@foo.bar, test2@foo.bar, ' + user.email,
    }
    response = client.post(url, data)
    assert redirect_target(response) == \
        'dashboard-{}-edit'.format(component.identifier)
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 2
    assert str(messages[0]) == (
        'Following users already accepted an invitation: ' + user.email)
    assert str(messages[1]) == ('2 moderators invited.')
    data = {
        'add_users': 'test1@foo.bar',
    }
    response = client.post(url, data)
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 4
    assert str(messages[2]) == (
        'Following users are already invited: test1@foo.bar')
    assert str(messages[3]) == ('0 moderators invited.')


@pytest.mark.django_db
def test_registered_user_gets_email_in_english(client, phase_factory, user):
    phase, module, project, idea = setup_phase(
        phase_factory, None, CollectFeedbackPhase)
    organisation = project.organisation
    organisation.language = 'de'
    organisation.save()
    url = component.get_base_url(project)
    initiator = module.project.organisation.initiators.first()
    client.login(username=initiator.email, password='password')
    response = client.get(url)
    assert_template_response(
        response, 'a4_candy_projects/project_moderators.html')

    data = {
        'add_users': user.email,
    }
    response = client.post(url, data)
    assert redirect_target(response) == \
        'dashboard-{}-edit'.format(component.identifier)
    assert ModeratorInvite.objects.get(email=user.email)
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject.startswith(
        'Invitation to moderate the project:')


@pytest.mark.django_db
def test_moderator_cannot_edit(client, phase_factory):
    phase, module, project, idea = setup_phase(
        phase_factory, None, CollectFeedbackPhase)
    url = component.get_base_url(project)
    moderator = project.moderators.first()
    client.login(username=moderator.email, password='password')
    response = client.get(url)
    assert response.status_code == 403

    data = {
        'add_users': 'test1@foo.bar,test2@foo.bar',
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_edit(client, phase_factory, user):
    phase, module, project, idea = setup_phase(
        phase_factory, None, CollectFeedbackPhase)
    url = component.get_base_url(project)
    client.login(username=user.email, password='password')
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_cannot_edit(client, phase_factory):
    phase, module, project, idea = setup_phase(
        phase_factory, None, CollectFeedbackPhase)
    url = component.get_base_url(project)
    response = client.get(url)
    assert response.status_code == 302
    assert redirect_target(response) == 'account_login'
