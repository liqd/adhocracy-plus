import pytest

from apps.mapideas import phases
from tests.helpers import assert_template_response
from tests.helpers import freeze_phase
from tests.helpers import setup_phase


@pytest.mark.django_db
def test_list_view_0(client, phase_factory, map_idea_factory, organisation):
    phase, module, project, item = setup_phase(
        phase_factory, map_idea_factory, phases.FeedbackPhase)
    url = project.get_absolute_url()
    with freeze_phase(phase):
        response = client.get(url)
        assert_template_response(
            response, 'a4_candy_mapideas/mapidea_list.html')


@pytest.mark.django_db
def test_list_view(client, phase_factory, map_idea_factory, organisation):
    phase, module, project, mapidea = setup_phase(
        phase_factory, map_idea_factory, phases.FeedbackPhase)
    phase_2, module_2, project_2, mapidea_2 = setup_phase(
        phase_factory, map_idea_factory, phases.FeedbackPhase)
    url = project.get_absolute_url()

    with freeze_phase(phase):
        response = client.get(url)
        assert_template_response(
            response, 'a4_candy_mapideas/mapidea_list.html')
        assert response.status_code == 200
        assert mapidea in response.context_data['mapidea_list']
        assert mapidea_2 not in response.context_data['mapidea_list']
        assert response.context_data['mapidea_list'][0].comment_count == 0
        assert (response.context_data['mapidea_list'][0].
                positive_rating_count == 0)
        assert (response.context_data['mapidea_list'][0].
                negative_rating_count == 0)
