import pytest
from django.urls import reverse
from rest_framework import status

from adhocracy4.polls import phases
from adhocracy4.polls.models import Answer
from adhocracy4.polls.models import Poll
from adhocracy4.polls.models import Vote
from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import setup_phase
from apps.projects.models import ProjectInsight


@pytest.mark.django_db
def test_project_with_single_poll_module_and_insights(
    client,
    phase_factory,
    answer_factory,
    open_question_factory,
    poll_factory,
    project_insight_factory,
):
    phase, poll, project, _ = setup_phase(
        phase_factory, poll_factory, phases.VotingPhase
    )

    project_insight = project_insight_factory(project=project)
    poll_answers = project_insight.poll_answers
    assert hasattr(project, "insight")

    poll = Poll.objects.first()
    question = open_question_factory(poll=poll)

    # post save signal in answer obj is called to increase the poll answer count
    answer_factory(question=question)
    project_insight.refresh_from_db()
    assert project_insight.poll_answers == poll_answers + 1

    url = reverse(
        "project-detail",
        kwargs={"slug": project.slug, "organisation_slug": project.organisation.slug},
    )

    response = client.get(url)
    assert "insight_label" in response.context_data.keys()


@pytest.mark.django_db
def test_normal_user_vote_is_added_as_participant(
    user, apiclient, poll_factory, phase_factory, question_factory, choice_factory
):

    phase, module, project, _ = setup_phase(
        phase_factory, poll_factory, phases.VotingPhase
    )

    poll = Poll.objects.first()
    question = question_factory(poll=poll)
    choice1 = choice_factory(question=question)
    choice_factory(question=question)
    open_question = question_factory(poll=poll, is_open=True)

    assert Vote.objects.count() == 0

    apiclient.force_authenticate(user=user)

    url = reverse("polls-vote", kwargs={"pk": poll.pk})

    data = {
        "votes": {
            question.pk: {
                "choices": [choice1.pk],
                "other_choice_answer": "",
                "open_answer": "",
            },
            open_question.pk: {
                "choices": [],
                "other_choice_answer": "",
                "open_answer": "an open answer",
            },
        },
        "agreed_terms_of_use": True,
    }

    with freeze_phase(phase):
        response = apiclient.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    insight = ProjectInsight.objects.first()

    assert Vote.objects.count() == 1
    assert Answer.objects.count() == 1
    assert insight.active_participants.count() == 1


@pytest.mark.django_db
def test_unregistered_user_vote_is_added_as_participant(
    user, apiclient, poll_factory, phase_factory, question_factory, choice_factory
):

    phase, module, project, _ = setup_phase(
        phase_factory, poll_factory, phases.VotingPhase
    )

    poll = Poll.objects.first()
    poll.allow_unregistered_users = True
    poll.save()
    question = question_factory(poll=poll)
    choice1 = choice_factory(question=question)
    choice_factory(question=question)
    open_question = question_factory(poll=poll, is_open=True)

    assert Vote.objects.count() == 0

    url = reverse("polls-vote", kwargs={"pk": poll.pk})

    data = {
        "votes": {
            question.pk: {
                "choices": [choice1.pk],
                "other_choice_answer": "",
                "open_answer": "",
            },
            open_question.pk: {
                "choices": [],
                "other_choice_answer": "",
                "open_answer": "an open answer",
            },
        },
        "agreed_terms_of_use": True,
        "captcha": "testpass:1",
    }

    with freeze_phase(phase):
        response = apiclient.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    insight = ProjectInsight.objects.first()

    assert Vote.objects.count() == 1
    assert Answer.objects.count() == 1
    assert insight.active_participants.count() == 0
    assert insight.unregistered_participants == 1
