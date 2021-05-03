import pytest
from dateutil.parser import parse
from django.urls import reverse
from freezegun import freeze_time

from apps.interactiveevents import phases
from tests.helpers import assert_template_response
from tests.helpers import setup_phase


@pytest.mark.django_db
def test_detail_view(client, user, phase_factory, live_question_factory,
                     interactive_extra_fields_factory):
    phase, module, project, live_question = setup_phase(
        phase_factory, live_question_factory, phases.IssuePhase,
        start_date=parse('2013-01-01 17:00:00 UTC'),
        end_date=parse('2013-01-01 19:00:00 UTC'))
    url = reverse(
        'live-question-module-detail',
        kwargs={
            'organisation_slug': project.organisation.slug,
            'module_slug': module.slug
        })

    with freeze_time(parse('2013-01-01 18:00:00 UTC')):
        response = client.get(url)
        assert_template_response(
            response,
            'a4_candy_interactive_events/livequestion_module_detail.html')
        assert 'Live now' not in response.content.decode()

    interactive_extra_fields = \
        interactive_extra_fields_factory(module=module, creator_id=user.id)
    interactive_extra_fields.live_stream = \
        '<div><div><iframe src="https://some.video" style=""></iframe>' \
        '</div></div>'
    interactive_extra_fields.save()

    with freeze_time(parse('2013-01-01 18:00:00 UTC')):
        response = client.get(url)
        assert_template_response(
            response,
            'a4_candy_interactive_events/livequestion_module_detail.html')
        assert 'Live now' in response.content.decode()

    with freeze_time(parse('2013-01-01 19:30:00 UTC')):
        response = client.get(url)
        assert_template_response(
            response,
            'a4_candy_interactive_events/livequestion_module_detail.html')
        assert 'Live now' not in response.content.decode()
