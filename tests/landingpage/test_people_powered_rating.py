import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_landing_page_shows_people_powered_rating_section(client):
    response = client.get(reverse("landing_page"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "lp-people-powered" in content
    assert "Trusted by People Powered" in content
    assert "https://www.peoplepowered.org/platform-ratings" in content
    assert "View full rating" in content
    assert "pp_smartphone.webp" in content
    assert "people-powered-badge.webp" in content
