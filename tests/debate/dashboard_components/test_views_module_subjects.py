import pytest
from django.urls import reverse

from adhocracy4.dashboard import components
from adhocracy4.test.helpers import redirect_target
from apps.debate.models import Subject
from apps.debate.phases import DebatePhase
from tests.helpers import assert_template_response
from tests.helpers import setup_phase

component = components.modules.get('subject_edit')


@pytest.mark.django_db
def test_edit_view(client, phase_factory, subject_factory):
    phase, module, project, item = setup_phase(
        phase_factory, subject_factory, DebatePhase)
    initiator = module.project.organisation.initiators.first()
    url = component.get_base_url(module)
    client.login(username=initiator.email, password='password')
    response = client.get(url)
    assert_template_response(response,
                             'a4_candy_debate/subject_dashboard_list.html')


@pytest.mark.django_db
def test_subject_create_view(client, phase_factory, category_factory):
    phase, module, project, item = setup_phase(
        phase_factory, None, DebatePhase)
    initiator = module.project.organisation.initiators.first()
    url = reverse(
        'a4dashboard:subject-create',
        kwargs={
            'organisation_slug': module.project.organisation.slug,
            'module_slug': module.slug
        })
    data = {
        'name': 'test'
    }
    client.login(username=initiator.email, password='password')
    response = client.post(url, data)
    assert redirect_target(response) == 'subject-list'
    subject = Subject.objects.get(name=data.get('name'))
    assert subject.name == 'test'


@pytest.mark.django_db
def test_subject_update_view(
        client, phase_factory, subject_factory, category_factory):
    phase, module, project, item = setup_phase(
        phase_factory, subject_factory, DebatePhase)
    initiator = module.project.organisation.initiators.first()
    url = reverse(
        'a4dashboard:subject-update',
        kwargs={
            'organisation_slug': item.module.project.organisation.slug,
            'pk': item.pk, 'year': item.created.year
        })
    data = {
        'name': 'test'
    }
    client.login(username=initiator.email, password='password')
    response = client.post(url, data)
    assert redirect_target(response) == 'subject-list'
    item.refresh_from_db()


@pytest.mark.django_db
def test_subject_delete_view(client, phase_factory, subject_factory):
    phase, module, project, item = setup_phase(
        phase_factory, subject_factory, DebatePhase)
    initiator = module.project.organisation.initiators.first()
    url = reverse(
        'a4dashboard:subject-delete',
        kwargs={
            'organisation_slug': item.module.project.organisation.slug,
            'pk': item.pk, 'year': item.created.year
        })
    client.login(username=initiator.email, password='password')
    response = client.delete(url)
    assert redirect_target(response) == 'subject-list'
    assert not Subject.objects.exists()
