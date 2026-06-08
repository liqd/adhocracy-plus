import pytest
from django.urls import reverse

from adhocracy4.test.helpers import assert_template_response
from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import setup_phase
from apps.budgeting import phases


@pytest.mark.django_db
def test_list_view(client, phase_factory, proposal_factory, organisation):
    phase, module, project, item = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    url = reverse(
        "module-detail",
        kwargs={
            "organisation_slug": project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        response = client.get(url)
        assert_template_response(response, "a4_candy_budgeting/proposal_list.html")
