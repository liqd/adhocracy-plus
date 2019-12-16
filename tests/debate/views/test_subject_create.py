import pytest
from django.urls import reverse

from adhocracy4.test.helpers import redirect_target
from apps.debate import models
from apps.debate import phases
from tests.helpers import assert_template_response
from tests.helpers import freeze_phase
from tests.helpers import freeze_pre_phase


@pytest.mark.django_db
def test_anonymous_cannot_create_topic(client, phase_factory):
    phase = phase_factory(phase_content=phases.DebatePhase())
    module = phase.module
    url = reverse(
        'a4dashboard:subject-create',
        kwargs={
            'organisation_slug': module.project.organisation.slug,
            'module_slug': module.slug
        })
    with freeze_phase(phase):
        count = models.Subject.objects.all().count()
        assert count == 0
        response = client.get(url)
        assert response.status_code == 302
        assert redirect_target(response) == 'account_login'


@pytest.mark.django_db
def test_user_cannot_create_topic(client, phase_factory, user):
    phase = phase_factory(phase_content=phases.DebatePhase())
    module = phase.module
    url = reverse(
        'a4dashboard:subject-create',
        kwargs={
            'organisation_slug': module.project.organisation.slug,
            'module_slug': module.slug
        })
    with freeze_phase(phase):
        response = client.get(url)
        assert response.status_code == 302
        client.login(username=user.email, password='password')
        response = client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_create_topic(client, phase_factory,
                                category_factory, admin):
    phase = phase_factory(phase_content=phases.DebatePhase())
    module = phase.module
    url = reverse(
        'a4dashboard:subject-create',
        kwargs={
            'organisation_slug': module.project.organisation.slug,
            'module_slug': module.slug
        })
    with freeze_phase(phase):
        client.login(username=admin.email, password='password')
        response = client.get(url)
        assert_template_response(
            response, 'a4_candy_debate/subject_create_form.html')
        assert response.status_code == 200
        subject = {
            'name': 'Subject'
        }
        response = client.post(url, subject)
        assert response.status_code == 302
        assert redirect_target(response) == 'subject-list'
        count = models.Subject.objects.all().count()
        assert count == 1


@pytest.mark.django_db
def test_moderator_can_create_topic_before_phase(client, phase_factory,
                                                 category_factory, admin):
    phase = phase_factory(phase_content=phases.DebatePhase())
    module = phase.module
    project = module.project
    moderator = project.moderators.first()
    url = reverse(
        'a4dashboard:subject-create',
        kwargs={
            'organisation_slug': module.project.organisation.slug,
            'module_slug': module.slug
        })
    with freeze_pre_phase(phase):
        client.login(username=moderator.email, password='password')
        response = client.get(url)
        assert_template_response(
            response, 'a4_candy_debate/subject_create_form.html')
        assert response.status_code == 200
        subject = {
            'name': 'Subject'
        }
        response = client.post(url, subject)
        assert response.status_code == 302
        assert redirect_target(response) == 'subject-list'
        count = models.Subject.objects.all().count()
        assert count == 1


@pytest.mark.django_db
def test_initiator_can_create_topic_before_phase(client, phase_factory,
                                                 category_factory, admin):
    phase = phase_factory(phase_content=phases.DebatePhase())
    module = phase.module
    project = module.project
    initiator = project.organisation.initiators.first()
    url = reverse(
        'a4dashboard:subject-create',
        kwargs={
            'organisation_slug': module.project.organisation.slug,
            'module_slug': module.slug
        })
    with freeze_pre_phase(phase):
        client.login(username=initiator.email, password='password')
        response = client.get(url)
        assert_template_response(
            response, 'a4_candy_debate/subject_create_form.html')
        assert response.status_code == 200
        subject = {
            'name': 'subject'
        }
        response = client.post(url, subject)
        assert response.status_code == 302
        assert redirect_target(response) == 'subject-list'
        count = models.Subject.objects.all().count()
        assert count == 1
