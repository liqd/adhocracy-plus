import pytest
from dateutil.parser import parse
from freezegun import freeze_time

from apps.questions import phases
from tests.helpers import assert_template_response
from tests.helpers import setup_phase


@pytest.mark.django_db
def test_detail_view(client, user, phase_factory, question_factory,
                     live_stream_factory):
    phase, module, project, question = setup_phase(
        phase_factory, question_factory, phases.IssuePhase,
        start_date=parse('2013-01-01 17:00:00 UTC'),
        end_date=parse('2013-01-01 19:00:00 UTC'))
    url = module.get_absolute_url()

    with freeze_time(parse('2013-01-01 18:00:00 UTC')):
        response = client.get(url)
        assert_template_response(
            response, 'a4_candy_questions/question_module_detail.html')
        assert '• Live now' not in response.content.decode()

    live_stream = live_stream_factory(module=module, creator_id=user.id)
    live_stream.live_stream = \
        '<div><div><iframe src="https://some.video" style=""></iframe>' \
        '</div></div>'
    live_stream.save()

    with freeze_time(parse('2013-01-01 18:00:00 UTC')):
        response = client.get(url)
        assert '• Live now' in response.content.decode()

    with freeze_time(parse('2013-01-01 19:30:00 UTC')):
        response = client.get(url)
        assert '• Live now' not in response.content.decode()
