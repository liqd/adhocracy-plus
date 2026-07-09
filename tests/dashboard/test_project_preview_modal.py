import pytest
from django.urls import reverse

from adhocracy4.test.helpers import assert_template_response
from adhocracy4.test.helpers import render_template


@pytest.mark.django_db
def test_project_preview_modal_view(client, project_factory, organisation):
    project = project_factory(organisation=organisation)
    initiator = organisation.initiators.first()
    url = reverse(
        "a4dashboard:project-preview-modal",
        kwargs={
            "organisation_slug": organisation.slug,
            "project_slug": project.slug,
        },
    )

    client.login(username=initiator.email, password="password")
    response = client.get(url)
    assert response.status_code == 200
    assert_template_response(
        response, "a4_candy_projects/partials/project_preview_modal_htmx.html"
    )
    content = response.content.decode()
    assert "<html" not in content
    assert "project-preview-modal__toggle" in content
    assert "project-preview-iframe" in content
    assert "data-content-url" in content
    assert "project-preview-content" not in content
    assert (
        reverse(
            "a4dashboard:project-preview-content",
            kwargs={
                "organisation_slug": organisation.slug,
                "project_slug": project.slug,
            },
        )
        in content
    )


@pytest.mark.django_db
def test_project_preview_content_view(client, project_factory, organisation):
    project = project_factory(organisation=organisation, name="Preview Test Project")
    initiator = organisation.initiators.first()
    url = reverse(
        "a4dashboard:project-preview-content",
        kwargs={
            "organisation_slug": organisation.slug,
            "project_slug": project.slug,
        },
    )

    client.login(username=initiator.email, password="password")
    response = client.get(url)
    assert response.status_code == 200
    assert_template_response(
        response, "a4_candy_projects/partials/project_preview_iframe.html"
    )
    content = response.content.decode()
    assert "<html" in content
    assert 'name="viewport"' in content
    assert "adhocracy4.css" in content
    assert 'id="main"' in content
    assert "container--shadow" in content
    assert "project-detail" in content
    assert "Preview Test Project" in content
    assert response.headers.get("X-Frame-Options") != "DENY"
    assert "project-subpage__edit" not in content


@pytest.mark.django_db
def test_project_preview_content_view_draft_banner(
    client, project_factory, organisation
):
    project = project_factory(organisation=organisation, is_draft=True)
    initiator = organisation.initiators.first()
    url = reverse(
        "a4dashboard:project-preview-content",
        kwargs={
            "organisation_slug": organisation.slug,
            "project_slug": project.slug,
        },
    )

    client.login(username=initiator.email, password="password")
    response = client.get(url)
    assert response.status_code == 200
    assert "info-box" in response.content.decode()


@pytest.mark.django_db
def test_preview_sidebar_renders_htmx_trigger(project_factory, organisation):
    project = project_factory(organisation=organisation)
    template = "{% load i18n %}" '{% include "a4dashboard/includes/preview.html" %}'
    content = render_template(
        template,
        {
            "project": project,
            "view": type("View", (), {"organisation": organisation})(),
        },
    )
    assert "hx-get" in content
    assert "/preview/modal/" in content
    assert "js-project-preview-trigger" in content


@pytest.mark.django_db
def test_project_information_hides_edit_button_in_iframe(
    client, project_factory, organisation
):
    project = project_factory(organisation=organisation)
    initiator = organisation.initiators.first()
    url = reverse(
        "project-information",
        kwargs={"organisation_slug": organisation.slug, "slug": project.slug},
    )

    client.login(username=initiator.email, password="password")
    response = client.get(url, HTTP_SEC_FETCH_DEST="iframe")
    assert response.status_code == 200
    content = response.content.decode()
    assert "project-subpage__edit" not in content


@pytest.mark.django_db
def test_project_information_allows_same_origin_framing(client, project_factory, user):
    project = project_factory(name="Framing Test Project")
    url = reverse(
        "project-information",
        kwargs={
            "organisation_slug": project.organisation.slug,
            "slug": project.slug,
        },
    )

    client.login(username=user.email, password="password")
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"


@pytest.mark.django_db
def test_project_preview_modal_view_forbidden_for_stranger(
    client, project_factory, organisation, user_factory
):
    project = project_factory(organisation=organisation)
    stranger = user_factory()
    url = reverse(
        "a4dashboard:project-preview-modal",
        kwargs={
            "organisation_slug": organisation.slug,
            "project_slug": project.slug,
        },
    )

    client.login(username=stranger.email, password="password")
    response = client.get(url)
    assert response.status_code == 403
