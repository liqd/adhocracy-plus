from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.projects.utils import is_ai_summarisation_enabled
from apps.summarization.models import ProjectSummary
from apps.summarization.pydantic_models import DocumentSummaryResponse
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


def project_generate_summary_url(project):
    return reverse(
        "project-generate-summary",
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
    assert "project-detail__summary" not in content
    assert "Summarize with AI" not in content


@pytest.mark.django_db
def test_project_detail_shows_summary_teaser_when_enabled(client, project_factory):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)

    response = client.get(project_detail_url(project))

    assert response.status_code == 200
    content = response.content.decode()
    assert "summary-card" in content
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
    assert "summary-card" not in content
    assert "summary__refresh-btn" in content


@pytest.mark.django_db
def test_project_generate_summary_denied_without_org_flag(client, project_factory):
    project = project_factory()
    response = client.get(project_generate_summary_url(project))

    assert response.status_code == 403


@pytest.mark.django_db
@patch("apps.projects.views.generate_project_summary")
def test_project_generate_summary_returns_html(generate_mock, client, project_factory):
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
    generate_mock.return_value = ProjectSummaryResponse(**summary_obj.response_data)

    response = client.get(project_generate_summary_url(project))

    assert response.status_code == 200
    assert "Generated overview" in response.content.decode()
    generate_mock.assert_called_once_with(
        project,
        request=generate_mock.call_args.kwargs["request"],
        allow_regeneration=False,
    )


@pytest.mark.django_db
@patch("apps.projects.views.generate_project_summary")
def test_project_generate_summary_without_cache_shows_error(
    generate_mock, client, project_factory
):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    generate_mock.return_value = None

    response = client.get(project_generate_summary_url(project))

    assert response.status_code == 200
    assert "Could not generate the summary" in response.content.decode()


@pytest.mark.django_db
@patch("apps.projects.views.generate_project_summary")
def test_project_generate_summary_refresh_updates_last_checked_at(
    generate_mock, client, project_factory
):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    summary_obj = ProjectSummary.objects.create(
        project=project,
        prompt="test",
        input_text_hash="hash",
        response_data=ProjectSummaryResponse(
            general_info=GeneralInfo(summary="Cached overview", goals=[]),
            phases=Phases(),
        ).model_dump(),
    )
    old_checked_at = timezone.now() - timedelta(hours=2)
    ProjectSummary.objects.filter(pk=summary_obj.pk).update(
        last_checked_at=old_checked_at
    )
    summary_obj.refresh_from_db()

    def refresh_cache(project, request=None, allow_regeneration=False, **kwargs):
        summary_obj.last_checked_at = timezone.now()
        summary_obj.save(update_fields=["last_checked_at"])
        return ProjectSummaryResponse(**summary_obj.response_data)

    generate_mock.side_effect = refresh_cache

    response = client.get(project_generate_summary_url(project))

    assert response.status_code == 200
    summary_obj.refresh_from_db()
    assert summary_obj.last_checked_at > old_checked_at
    assert "Refresh" in response.content.decode()


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
@patch("apps.projects.views.generate_project_summary")
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
        "request": generate_mock.call_args.kwargs["request"],
        "allow_regeneration": True,
        "force_regeneration": True,
    }


@pytest.mark.django_db
def test_project_summary_feedback_requires_enabled_org(client, project_factory):
    project = project_factory()
    response = client.post(
        project_summary_feedback_url(project),
        data={"summary_id": 1, "feedback": "positive"},
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
        data={"summary_id": summary.pk, "feedback": "positive"},
    )

    assert response.status_code == 200
    assert summary.feedback.filter(user=user, feedback="positive").exists()


@pytest.mark.django_db
@patch("apps.projects.utils.collect_document_attachments")
@patch("apps.projects.utils.AIService")
def test_generate_project_summary_excludes_images_by_default(
    service_mock, collect_mock, project_factory
):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    collect_mock.return_value = (
        {"project_information_attachment_0": "https://example.org/photo.jpg"},
        {"project_information_attachment_0": "project_information"},
    )
    service_mock.return_value.request_vision_dict.return_value = (
        DocumentSummaryResponse(documents=[])
    )
    service_mock.return_value.project_summarize.return_value = ProjectSummaryResponse(
        general_info=GeneralInfo(summary="Overview", goals=[]),
        phases=Phases(),
    )

    from apps.projects.utils import generate_project_summary

    generate_project_summary(project, base_url="https://example.org")

    vision_call = service_mock.return_value.request_vision_dict
    assert vision_call.call_args.kwargs["include_images"] is False


@pytest.mark.django_db
@patch("apps.projects.utils.collect_document_attachments")
@patch("apps.projects.utils.AIService")
def test_generate_project_summary_includes_images_when_global_setting_enabled(
    service_mock, collect_mock, project_factory
):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    collect_mock.return_value = (
        {"project_information_attachment_0": "https://example.org/photo.jpg"},
        {"project_information_attachment_0": "project_information"},
    )
    service_mock.return_value.request_vision_dict.return_value = (
        DocumentSummaryResponse(documents=[])
    )
    service_mock.return_value.project_summarize.return_value = ProjectSummaryResponse(
        general_info=GeneralInfo(summary="Overview", goals=[]),
        phases=Phases(),
    )

    from apps.contrib.models import Settings
    from apps.projects.utils import generate_project_summary

    Settings.objects.update_or_create(
        key="project_summary_include_images",
        defaults={"value": "true"},
    )

    generate_project_summary(project, base_url="https://example.org")

    vision_call = service_mock.return_value.request_vision_dict
    assert vision_call.call_args.kwargs["include_images"] is True
