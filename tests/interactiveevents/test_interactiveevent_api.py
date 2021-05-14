import pytest
from django.urls import reverse

from apps.interactiveevents import models
from apps.interactiveevents import phases
from tests.helpers import freeze_phase
from tests.helpers import freeze_post_phase
from tests.helpers import freeze_pre_phase
from tests.helpers import setup_phase


@pytest.mark.django_db
def test_anonymous_can_create_livequestion_during_active_phase(
        apiclient, category_factory, phase_factory):

    phase = phase_factory(phase_content=phases.IssuePhase())
    module = phase.module
    category = category_factory(module=module)
    url = reverse('interactiveevents-list',
                  kwargs={'module_pk': module.pk})
    data = {
        'text': 'I have a question',
        'category': category.pk
    }
    with freeze_phase(phase):
        response = apiclient.post(url, data, format='json')
        assert response.status_code == 201

    live_question = models.LiveQuestion.objects.first()
    assert live_question.text == 'I have a question'
    assert live_question.category == category


@pytest.mark.django_db
def test_user_cannot_create_livequestion_during_pre_phase(
        apiclient, user, category_factory, phase_factory):

    phase = phase_factory(phase_content=phases.IssuePhase())
    module = phase.module
    category = category_factory(module=module)
    url = reverse('interactiveevents-list',
                  kwargs={'module_pk': module.pk})
    data = {
        'text': 'I have a question',
        'category': category.pk
    }
    assert apiclient.login(username=user.email, password='password')
    with freeze_pre_phase(phase):
        response = apiclient.post(url, data, format='json')
        assert response.status_code == 403


@pytest.mark.django_db
def test_initiator_cannot_create_livequestion_during_post_phase(
        apiclient, category_factory, phase_factory):

    phase = phase_factory(phase_content=phases.IssuePhase())
    module = phase.module
    category = category_factory(module=module)
    initiator = module.project.organisation.initiators.first()
    url = reverse('interactiveevents-list',
                  kwargs={'module_pk': module.pk})
    data = {
        'text': 'I have a question',
        'category': category.pk
    }
    assert apiclient.login(username=initiator.email, password='password')
    with freeze_post_phase(phase):
        response = apiclient.post(url, data, format='json')
        assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_can_view_and_cannot_change_questions(apiclient,
                                                        phase_factory,
                                                        live_question_factory):

    phase, module, project, livequestion = setup_phase(phase_factory,
                                                       live_question_factory,
                                                       phases.IssuePhase)

    url = reverse('interactiveevents-list', kwargs={'module_pk': module.pk})
    url_detail = reverse('interactiveevents-detail',
                         kwargs={'module_pk': module.pk,
                                 'pk': livequestion.pk})

    data = {
        'text': livequestion.text,
        'category': livequestion.category.pk,
        'is_hidden': True
    }

    response = apiclient.get(url)
    assert response.status_code == 200

    response = apiclient.put(url_detail, data, format='json')
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderator_can_view_and_change_questions(apiclient,
                                                 phase_factory,
                                                 live_question_factory):
    phase, module, project, livequestion = setup_phase(phase_factory,
                                                       live_question_factory,
                                                       phases.IssuePhase)

    url = reverse('interactiveevents-list', kwargs={'module_pk': module.pk})
    url_detail = reverse('interactiveevents-detail',
                         kwargs={'module_pk': module.pk,
                                 'pk': livequestion.pk})

    data = {
        'text': livequestion.text,
        'category': livequestion.category.pk,
        'is_hidden': True
    }

    moderator = project.moderators.first()
    apiclient.force_authenticate(user=moderator)

    response = apiclient.get(url)
    assert response.status_code == 200

    assert len(models.LiveQuestion.objects.filter(is_hidden=True)) == 0
    response = apiclient.put(url_detail, data, format='json')
    assert response.status_code == 200

    assert len(models.LiveQuestion.objects.all()) == 1
    question_changed = models.LiveQuestion.objects.first()
    assert question_changed.is_hidden


@pytest.mark.django_db
def test_anonymous_can_add_like_during_active_phase(apiclient,
                                                    phase_factory,
                                                    live_question_factory):

    phase, module, project, livequestion = setup_phase(phase_factory,
                                                       live_question_factory,
                                                       phases.IssuePhase)

    url = reverse('likes-list', kwargs={'livequestion_pk': livequestion.pk})
    data = {'value': True}
    with freeze_phase(phase):
        response = apiclient.post(url, data)

    assert response.status_code == 201
    assert models.Like.objects.count() == 1


@pytest.mark.django_db
def test_user_cannot_add_like_during_non_active_phase(apiclient,
                                                      phase_factory,
                                                      live_question_factory,
                                                      user):

    phase, module, project, livequestion = setup_phase(phase_factory,
                                                       live_question_factory,
                                                       phases.IssuePhase)

    url = reverse('likes-list', kwargs={'livequestion_pk': livequestion.pk})
    assert apiclient.login(username=user.email, password='password')

    data = {'value': True}
    with freeze_pre_phase(phase):
        response = apiclient.post(url, data)

    assert response.status_code == 403
    assert models.Like.objects.count() == 0

    with freeze_post_phase(phase):
        response = apiclient.post(url, data)

    assert response.status_code == 403
    assert models.Like.objects.count() == 0
