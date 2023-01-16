import pytest
from django.urls import reverse

from adhocracy4.test.helpers import assert_template_response
from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import redirect_target
from adhocracy4.test.helpers import setup_phase
from apps.budgeting import phases


@pytest.mark.django_db
def test_moderate_view(
    client, phase_factory, proposal_factory, user, area_settings_factory
):
    phase, module, project, item = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    area_settings_factory(module=module)
    url = reverse(
        "a4_candy_budgeting:proposal-moderate",
        kwargs={
            "organisation_slug": project.organisation.slug,
            "pk": item.pk,
            "year": item.created.year,
        },
    )
    project.moderators.set([user])
    with freeze_phase(phase):
        client.login(username=user.email, password="password")

        response = client.get(url)
        assert_template_response(
            response, "a4_candy_budgeting/proposal_moderate_form.html"
        )

        data = {
            "moderator_status": "test",
            "is_archived": False,
            "moderator_feedback_text": "its a feedback text",
        }
        response = client.post(url, data)
        assert redirect_target(response) == "proposal-detail"
