import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_project_list_shows_initiator_help_card(client, organisation):
    initiator = organisation.initiators.first()
    url = reverse(
        "a4dashboard:project-list",
        kwargs={"organisation_slug": organisation.slug},
    )

    client.login(username=initiator.email, password="password")
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode()
    assert "dashboard-help-card" in content
    assert "Get the most out of" in content
    assert "adhocracy.plus" in content
    assert "/info/additional-services/" in content
    assert "Download price list" in content
