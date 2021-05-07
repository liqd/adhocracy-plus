import pytest

from adhocracy4.dashboard import components
from apps.interactiveevents.phases import IssuePhase
from tests.helpers import assert_template_response
from tests.helpers import setup_phase

component = components.modules.get('extra_fields')


@pytest.mark.django_db
def test_extrafields_dashboard_view(client, phase_factory):
    phase, module, project, item = setup_phase(
        phase_factory, None, IssuePhase)
    initiator = module.project.organisation.initiators.first()
    url = component.get_base_url(module)
    client.login(username=initiator.email, password='password')
    response = client.get(url)

    labels = [entry['label'] for entry in
              response.context_data['dashboard_menu']['modules'][0]['menu']]
    assert 'Media' in labels
    assert_template_response(
        response,
        'a4_candy_interactive_events/extrafields_dashboard_form.html')
    assert 'live_stream' in response.context_data['form'].fields
    assert 'event_image' in response.context_data['form'].fields

    data = {'live_stream': '<div>Livestram data</div>',
            # that doesnt work
            # 'event_image': ImagePNG
            }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == url

    response = client.get(url)
    assert response.status_code == 200
    assert 'extrafieldsinteractiveevent' in response.context_data
    assert response.context_data['extrafieldsinteractiveevent'].\
           live_stream == data['live_stream']
