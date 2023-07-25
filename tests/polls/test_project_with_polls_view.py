import pytest
from django.urls import reverse

from adhocracy4.test.helpers import setup_phase
from apps.interactiveevents import phases
from apps.projects.insights import create_insight


@pytest.mark.django_db
def test_project_with_single_poll_module_and_insights(
    client, phase_factory, poll_factory
):
    phase, module, project, _ = setup_phase(phase_factory, None, phases.IssuePhase)

    create_insight(project=project)
    assert hasattr(project, "insight")
    project.insight.display = True
    project.insight.save()

    url = reverse(
        "project-detail",
        kwargs={"slug": project.slug, "organisation_slug": project.organisation.slug},
    )

    response = client.get(url)
    assert "insight_label" in response.context_data.keys()
