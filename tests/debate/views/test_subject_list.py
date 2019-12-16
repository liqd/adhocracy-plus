import pytest

from apps.debate import phases
from tests.helpers import assert_template_response
from tests.helpers import freeze_phase
from tests.helpers import setup_phase


@pytest.mark.django_db
def test_list_view(client, phase_factory, subject_factory):
    phase, module, project, subject = setup_phase(
        phase_factory, subject_factory, phases.DebatePhase)
    phase_2, module_2, project_2, subject_2 = setup_phase(
        phase_factory, subject_factory, phases.DebatePhase)
    url = project.get_absolute_url()

    with freeze_phase(phase):
        response = client.get(url)
        assert_template_response(
            response, 'a4_candy_debate/subject_list.html')
        assert response.status_code == 200
        assert subject in response.context_data['subject_list']
        assert subject_2 not in response.context_data['subject_list']
        assert response.context_data['subject_list'][0].comment_count == 0
