import pytest
from django.urls import reverse

from apps.likes.models import Like
from apps.questions import phases
from tests.helpers import assert_template_response
from tests.helpers import freeze_phase
from tests.helpers import setup_phase


@pytest.mark.django_db
def test_presentation_list_view(client, user, phase_factory,
                                like_factory, question_factory):
    phase, module, project, question = setup_phase(
        phase_factory, question_factory, phases.IssuePhase)
    phase_2, module_2, project_2, question_2 = setup_phase(
        phase_factory, question_factory, phases.IssuePhase)

    like_factory(question=question)
    assert Like.objects.all().count() == \
           len(question.question_likes.all())

    url = reverse('question-present',
                  kwargs={'module_slug': module.slug,
                          'organisation_slug':
                              module.project.organisation.slug})

    moderator = module.project.moderators.first()

    with freeze_phase(phase):
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == '/accounts/login/?next=' + url

        client.login(username=user.email, password='password')
        response = client.get(url)
        assert response.status_code == 403

        client.login(username=moderator.email, password='password')
        response = client.get(url)
        assert_template_response(
            response, 'a4_candy_questions/question_present_list.html')

        assert question in response.context_data['question_list']
        assert question_2 not in \
               response.context_data['question_list']

        assert len(response.context_data['object_list'].all()) == 1
        assert response.context_data['object_list'][0] == question
