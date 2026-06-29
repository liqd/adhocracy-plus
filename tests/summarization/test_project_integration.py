import json
from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.summarization.models import ProjectSummary
from apps.summarization.project_summary import is_ai_summarisation_enabled
from apps.summarization.pydantic_models import GeneralInfo
from apps.summarization.pydantic_models import Phases
from apps.summarization.pydantic_models import ProjectSummaryResponse
from tests.factories import OrganisationFactory
from tests.factories import UserFactory


def project_detail_url(project):
    return reverse(
        "project-detail",
        kwargs={
            "slug": project.slug,
            "organisation_slug": project.organisation.slug,
        },
    )


def project_summary_url(project):
    return reverse(
        "project-summary",
        kwargs={
            "slug": project.slug,
            "organisation_slug": project.organisation.slug,
        },
    )


def project_summary_feedback_url(project):
    return reverse(
        "project-summary-feedback",
        kwargs={
            "slug": project.slug,
            "organisation_slug": project.organisation.slug,
        },
    )


def project_summary_generate_url(project):
    return reverse(
        "project-summary-generate",
        kwargs={
            "slug": project.slug,
            "organisation_slug": project.organisation.slug,
        },
    )


@pytest.mark.django_db
def test_is_ai_summarisation_enabled_requires_org_flag(project_factory):
    project = project_factory()
    assert is_ai_summarisation_enabled(project) is False

    project.organisation.enable_ai_summarisation = True
    project.organisation.save()
    assert is_ai_summarisation_enabled(project) is True


@pytest.mark.django_db
def test_project_detail_hides_summary_without_org_flag(client, project_factory):
    project = project_factory()
    response = client.get(project_detail_url(project))

    assert response.status_code == 200
    content = response.content.decode()
    assert "data-project-summary" not in content
    assert "Summarize with AI" not in content


@pytest.mark.django_db
def test_project_detail_shows_summary_teaser_when_enabled(client, project_factory):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)

    response = client.get(project_detail_url(project))

    assert response.status_code == 200
    content = response.content.decode()
    assert "data-project-summary" in content
    assert "Summarize with AI" in content
    assert "Summary of the participation" in content


@pytest.mark.django_db
def test_project_detail_shows_cached_summary(client, project_factory):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    response_data = ProjectSummaryResponse(
        general_info=GeneralInfo(summary="Cached overview", goals=["Goal A"]),
        phases=Phases(),
    ).model_dump()
    ProjectSummary.objects.create(
        project=project,
        prompt="test",
        input_text_hash="abc",
        response_data=response_data,
    )

    response = client.get(project_detail_url(project))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Cached overview" in content
    assert "data-project-summary-generate" not in content


@pytest.mark.django_db
def test_project_summary_endpoint_denied_without_org_flag(client, project_factory):
    project = project_factory()
    response = client.post(project_summary_url(project))

    assert response.status_code == 403


@pytest.mark.django_db
@patch("apps.summarization.project_views.generate_project_summary")
def test_project_summary_endpoint_returns_cached_summary(
    generate_mock, client, project_factory
):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    summary_obj = ProjectSummary.objects.create(
        project=project,
        prompt="test",
        input_text_hash="hash",
        response_data=ProjectSummaryResponse(
            general_info=GeneralInfo(summary="Generated overview", goals=[]),
            phases=Phases(),
        ).model_dump(),
    )
    generate_mock.return_value = (
        ProjectSummaryResponse(**summary_obj.response_data),
        summary_obj,
    )

    response = client.post(project_summary_url(project))

    assert response.status_code == 200
    payload = response.json()
    assert payload["has_summary"] is True
    assert "Generated overview" in payload["html"]
    assert payload["summary_id"] == summary_obj.pk
    generate_mock.assert_called_once_with(project, allow_regeneration=False)


@pytest.mark.django_db
@patch("apps.summarization.project_views.generate_project_summary")
def test_project_summary_endpoint_without_cache_returns_empty(
    generate_mock, client, project_factory
):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    generate_mock.return_value = (None, None)

    response = client.post(project_summary_url(project))

    assert response.status_code == 200
    assert response.json() == {"has_summary": False}


@pytest.mark.django_db
def test_project_summary_generate_requires_staff(client, project_factory):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)

    response = client.get(project_summary_generate_url(project))
    assert response.status_code == 302
    assert "/login" in response.url


@pytest.mark.django_db
def test_project_summary_generate_denies_non_staff(client, project_factory):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    user = UserFactory()
    client.force_login(user)

    response = client.get(project_summary_generate_url(project))
    assert response.status_code == 403


@pytest.mark.django_db
@patch("apps.summarization.project_views.generate_project_summary")
def test_project_summary_generate_triggers_for_staff(
    generate_mock, client, project_factory
):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    admin = UserFactory(is_staff=True, is_superuser=True)
    client.force_login(admin)

    response = client.get(project_summary_generate_url(project))

    assert response.status_code == 302
    assert response.url == project_detail_url(project)
    generate_mock.assert_called_once()
    (called_project,) = generate_mock.call_args.args
    assert called_project.pk == project.pk
    assert generate_mock.call_args.kwargs == {
        "allow_regeneration": True,
        "force_regeneration": True,
    }


@pytest.mark.django_db
def test_project_summary_feedback_requires_enabled_org(client, project_factory):
    project = project_factory()
    response = client.post(
        project_summary_feedback_url(project),
        data=json.dumps({"summary_id": 1, "feedback": "positive"}),
        content_type="application/json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_summary_feedback_stores_vote(client, project_factory):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    user = UserFactory()
    client.force_login(user)
    summary = ProjectSummary.objects.create(
        project=project,
        prompt="test",
        input_text_hash="hash",
        response_data=ProjectSummaryResponse(
            general_info=GeneralInfo(summary="Overview", goals=[]),
            phases=Phases(),
        ).model_dump(),
    )

    response = client.post(
        project_summary_feedback_url(project),
        data=json.dumps({"summary_id": summary.pk, "feedback": "positive"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert summary.feedback.filter(user=user, feedback="positive").exists()
