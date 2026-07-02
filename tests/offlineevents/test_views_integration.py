import pytest
from dateutil.parser import parse

from adhocracy4.test.helpers import assert_template_response


@pytest.mark.django_db
def test_detail_view(client, offline_event, module_factory, phase_factory):
    module = module_factory(project=offline_event.project)
    phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )
    response = client.get(offline_event.get_absolute_url())
    assert_template_response(
        response, "a4_candy_offlineevents/offlineevent_detail.html"
    )
    assert offline_event.name.encode() in response.content
    assert b"item-detail__title" in response.content
    assert b"data-participation-view" not in response.content
    assert offline_event.project.get_absolute_url().encode() in response.content
    assert b"platform-breadcrumbs__link" in response.content
    assert b"platform-breadcrumbs__current" in response.content
