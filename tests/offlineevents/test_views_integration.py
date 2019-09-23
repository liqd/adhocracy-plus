import pytest

from tests.helpers import assert_template_response


@pytest.mark.django_db
def test_detail_view(client, offline_event, organisation):
    url = offline_event.get_absolute_url()
    response = client.get(url)
    assert_template_response(
        response, 'a4_candy_projects/project_detail.html')
