import pytest
from django.urls import reverse

from apps.interactiveevents import models
from apps.interactiveevents import phases
from tests.helpers import setup_phase


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
