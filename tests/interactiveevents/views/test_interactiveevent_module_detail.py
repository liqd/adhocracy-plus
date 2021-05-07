import pytest
from django.urls import reverse

from apps.interactiveevents import phases
from tests.helpers import assert_template_response
from tests.helpers import setup_phase


@pytest.mark.django_db
def test_module_detail_view(client, phase_factory, live_question_factory):
    phase, module, project, _ = setup_phase(
        phase_factory, None, phases.IssuePhase)
    url = reverse(
        'module-detail',
        kwargs={
            'organisation_slug': project.organisation.slug,
            'module_slug': module.slug
        })

    response = client.get(url)
    assert_template_response(response,
                             'a4_candy_interactive_events/module_detail.html')
    assert 'extra_fields' in response.context_data
