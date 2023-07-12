import pytest
from django.urls import reverse

from adhocracy4.polls import phases
from adhocracy4.polls.models import Poll
from adhocracy4.test.helpers import setup_phase


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
    assert hasattr(project, "insight")

    poll = Poll.objects.first()
    question = open_question_factory(poll=poll)

    # post save signal in answer obj is called for
    # adding the creator of the answer to the insights
    answer = answer_factory(question=question)

    assert project_insight.active_participants.first() == answer.creator

    url = reverse(
        "project-detail",
        kwargs={"slug": project.slug, "organisation_slug": project.organisation.slug},
    )

    response = client.get(url)
    assert "insight_label" in response.context_data.keys()
