import pytest
from django.urls import reverse

from adhocracy4.test.helpers import assert_template_response
from adhocracy4.test.helpers import setup_phase
from apps.interactiveevents import phases
from apps.projects.insights import create_insight


@pytest.mark.django_db
def test_module_detail_view(client, phase_factory, live_question_factory):
    phase, module, project, _ = setup_phase(phase_factory, None, phases.IssuePhase)

    url = reverse(
        "module-detail",
        kwargs={
            "organisation_slug": project.organisation.slug,
            "module_slug": module.slug,
        },
    )

    response = client.get(url)
    assert_template_response(response, "a4_candy_interactive_events/module_detail.html")
    assert "extra_fields" in response.context_data


@pytest.mark.django_db
def test_module_detail_view_with_insights(client, phase_factory, live_question_factory):
    phase, module, project, _ = setup_phase(phase_factory, None, phases.IssuePhase)

    create_insight(project=project)
    assert hasattr(project, "insight")

    url = reverse(
        "module-detail",
        kwargs={
            "organisation_slug": project.organisation.slug,
            "module_slug": module.slug,
        },
    )

    response = client.get(url)
    assert_template_response(response, "a4_candy_interactive_events/module_detail.html")
    assert "extra_fields" in response.context_data
    assert "insight_label" not in response.context_data.keys()

    project.insight.display = True
    project.insight.save()
    response = client.get(url)
    assert "insight_label" in response.context_data.keys()
