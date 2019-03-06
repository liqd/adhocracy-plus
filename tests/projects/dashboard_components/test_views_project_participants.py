import pytest

from adhocracy4.dashboard import components
from adhocracy4.test.helpers import redirect_target
from liqd_product.apps.ideas.phases import CollectFeedbackPhase
from liqd_product.apps.projects.models import ParticipantInvite
from tests.helpers import assert_template_response
from tests.helpers import setup_phase

component = components.projects.get('participants')


@pytest.mark.django_db
def test_initiator_can_edit(client, phase_factory):
    phase, module, project, idea = setup_phase(
        phase_factory, None, CollectFeedbackPhase)
    url = component.get_base_url(project)
    initiator = module.project.organisation.initiators.first()
    client.login(username=initiator.email, password='password')
    response = client.get(url)
    assert_template_response(
        response, 'liqd_product_projects/project_participants.html')

    data = {
        'add_users': 'test1@foo.bar,test2@foo.bar',
    }
    response = client.post(url, data)
    assert redirect_target(response) == \
        'dashboard-{}-edit'.format(component.identifier)
    assert ParticipantInvite.objects.get(email='test1@foo.bar')
    assert ParticipantInvite.objects.get(email='test2@foo.bar')


@pytest.mark.django_db
def test_moderator_can_edit(client, phase_factory):
    phase, module, project, idea = setup_phase(
        phase_factory, None, CollectFeedbackPhase)
    url = component.get_base_url(project)
    moderator = project.moderators.first()
    client.login(username=moderator.email, password='password')
    response = client.get(url)
    assert_template_response(
        response, 'liqd_product_projects/project_participants.html')

    data = {
        'add_users': 'test1@foo.bar,test2@foo.bar',
    }
    response = client.post(url, data)
    assert redirect_target(response) == \
        'dashboard-{}-edit'.format(component.identifier)
    assert ParticipantInvite.objects.get(email='test1@foo.bar')
    assert ParticipantInvite.objects.get(email='test2@foo.bar')


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
