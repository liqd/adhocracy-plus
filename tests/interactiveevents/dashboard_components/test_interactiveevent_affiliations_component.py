import pytest

from adhocracy4.dashboard import components
from adhocracy4.test.helpers import assert_template_response
from adhocracy4.test.helpers import setup_phase
from apps.interactiveevents.phases import IssuePhase

component = components.modules.get("affiliations")


@pytest.mark.django_db
def test_affiliations_required(client, phase_factory, category_factory):
    phase, module, project, item = setup_phase(phase_factory, None, IssuePhase)
    module.blueprint_type = "IE"
    module.save()
    initiator = module.project.organisation.initiators.first()
    url = component.get_base_url(module)
    client.login(username=initiator.email, password="password")
    response = client.get(url)
    assert_template_response(response, "a4dashboard/base_form_module.html")

    progress = response.context_data["project_progress"]
    assert progress["valid"] == progress["required"] - 1

    category_factory(module=module)
    response = client.get(url)
    progress = response.context_data["project_progress"]
    assert progress["valid"] == progress["required"]
