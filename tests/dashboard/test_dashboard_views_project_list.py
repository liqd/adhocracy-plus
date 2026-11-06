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


@pytest.mark.django_db
def test_single_organisation_header_links_organisation_name(client, organisation):
    initiator = organisation.initiators.first()
    url = reverse(
        "a4dashboard:project-list",
        kwargs={"organisation_slug": organisation.slug},
    )

    client.login(username=initiator.email, password="password")
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode()
    organisation_url = reverse(
        "organisation", kwargs={"organisation_slug": organisation.slug}
    )

    assert "dashboard-nav__organisation-link" in content
    assert f'href="{organisation_url}"' in content
    assert "dashboard-nav__organisation-name" in content
    assert "organisation-selection" not in content
    assert "fa-external-link-alt" in content


@pytest.mark.django_db
def test_multi_organisation_header_shows_live_button(
    client, organisation, organisation_factory
):
    initiator = organisation.initiators.first()
    organisation_factory(initiators=[initiator])
    url = reverse(
        "a4dashboard:project-list",
        kwargs={"organisation_slug": organisation.slug},
    )

    client.login(username=initiator.email, password="password")
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode()
    organisation_url = reverse(
        "organisation", kwargs={"organisation_slug": organisation.slug}
    )

    # The organisation dropdown stays unchanged.
    assert "organisation-selection" in content
    # A separate button links to the live page and opens it in a new tab.
    assert "dashboard-nav__live-button" in content
    assert f'href="{organisation_url}"' in content
    assert 'target="_blank"' in content
    assert 'rel="noopener noreferrer"' in content
    assert "fa-external-link-alt" in content
    assert "View Live" in content
