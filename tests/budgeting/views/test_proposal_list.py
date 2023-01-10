import pytest

from adhocracy4.test.helpers import assert_template_response
from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import setup_phase
from apps.budgeting import phases


@pytest.mark.django_db
def test_list_view(client, phase_factory, proposal_factory, organisation):
    phase, module, project, item = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    url = project.get_absolute_url()
    with freeze_phase(phase):
        response = client.get(url)
        assert_template_response(response, "a4_candy_budgeting/proposal_list.html")
