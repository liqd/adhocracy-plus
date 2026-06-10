import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_detail_view_redirects_to_project_timeline(client, offline_event):
    detail_url = reverse(
        "a4_candy_offlineevents:offlineevent-detail",
        kwargs={
            "organisation_slug": offline_event.project.organisation.slug,
            "slug": offline_event.slug,
        },
    )
    response = client.get(detail_url)
    assert response.status_code == 302
    assert response.url == offline_event.get_absolute_url()
