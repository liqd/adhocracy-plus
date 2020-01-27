import pytest
from django.urls import reverse

from apps.debate import phases
from tests.helpers import freeze_phase


@pytest.mark.django_db
def test_user_cannot_export_subjects(client, phase_factory,
                                     user):
    phase = phase_factory(phase_content=phases.DebatePhase())
    module = phase.module
    client.login(username=user.email, password='password')
    url = reverse(
        'a4dashboard:subject-export-module',
        kwargs={
            'organisation_slug': module.project.organisation.slug,
            'module_slug': module.slug
        })
    with freeze_phase(phase):
        response = client.get(url)
        assert response.status_code == 403
        export_url = reverse(
            'a4dashboard:subject-export',
            kwargs={
                'organisation_slug': module.project.organisation.slug,
                'module_slug': module.slug
            })
        response = client.get(export_url)
        assert response.status_code == 403


@pytest.mark.django_db
def test_initiator_can_export_subjects(client, phase_factory):
    phase = phase_factory(phase_content=phases.DebatePhase())
    module = phase.module
    initiator = module.project.organisation.initiators.first()
    client.login(username=initiator.email, password='password')
    url = reverse(
        'a4dashboard:subject-export-module',
        kwargs={
            'organisation_slug': module.project.organisation.slug,
            'module_slug': module.slug
        })
    with freeze_phase(phase):
        response = client.get(url)
        assert response.status_code == 200
        export_url = reverse(
            'a4dashboard:subject-export',
            kwargs={
                'organisation_slug': module.project.organisation.slug,
                'module_slug': module.slug
            })
        assert response.context['export'] == export_url
        response = client.get(export_url)
        assert response.status_code == 200
        assert 'application/vnd.openxmlformats-officedocument.'\
            'spreadsheetml.sheet' == response['Content-Type']


@pytest.mark.django_db
def test_user_cannot_export_subject_comments(client, phase_factory,
                                             user):
    phase = phase_factory(phase_content=phases.DebatePhase())
    module = phase.module
    client.login(username=user.email, password='password')
    with freeze_phase(phase):
        export_url = reverse(
            'a4dashboard:subject-comment-export',
            kwargs={
                'organisation_slug': module.project.organisation.slug,
                'module_slug': module.slug
            })
        response = client.get(export_url)
        assert response.status_code == 403


@pytest.mark.django_db
def test_initiator_can_export_subject_comments(client, phase_factory):
    phase = phase_factory(phase_content=phases.DebatePhase())
    module = phase.module
    initiator = module.project.organisation.initiators.first()
    client.login(username=initiator.email, password='password')
    url = reverse(
        'a4dashboard:subject-export-module',
        kwargs={
            'organisation_slug': module.project.organisation.slug,
            'module_slug': module.slug
        })
    with freeze_phase(phase):
        response = client.get(url)
        assert response.status_code == 200
        export_url = reverse(
            'a4dashboard:subject-comment-export',
            kwargs={
                'organisation_slug': module.project.organisation.slug,
                'module_slug': module.slug
            })
        assert response.context['comment_export'] == export_url
        response = client.get(export_url)
        assert response.status_code == 200
        assert 'application/vnd.openxmlformats-officedocument.'\
            'spreadsheetml.sheet' == response['Content-Type']
