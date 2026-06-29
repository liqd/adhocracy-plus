from datetime import timedelta
from unittest.mock import patch

import pytest
from django.test.utils import override_settings
from django.utils import timezone

from apps.summarization.models import ProjectSummary
from apps.summarization.project_summary import project_needs_summary_refresh
from apps.summarization.tasks import get_projects_due_for_summary_refresh
from apps.summarization.tasks import refresh_project_summaries
from apps.summarization.tasks import refresh_project_summary
from tests.factories import OrganisationFactory


@pytest.mark.django_db
@override_settings(PROJECT_SUMMARY_AUTO_REFRESH_MAX_AGE_MINUTES=720)
def test_project_needs_summary_refresh_without_cache(project_factory):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)

    assert project_needs_summary_refresh(project) is True


@pytest.mark.django_db
@override_settings(PROJECT_SUMMARY_AUTO_REFRESH_MAX_AGE_MINUTES=720)
def test_project_needs_summary_refresh_when_cache_is_stale(project_factory):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    ProjectSummary.objects.create(
        project=project,
        prompt="test",
        input_text_hash="stale-hash",
        response_data={"title": "Summary"},
        created_at=timezone.now() - timedelta(hours=13),
    )

    assert project_needs_summary_refresh(project) is True


@pytest.mark.django_db
@override_settings(PROJECT_SUMMARY_AUTO_REFRESH_MAX_AGE_MINUTES=720)
def test_project_needs_summary_refresh_when_export_hash_changed(project_factory):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    ProjectSummary.objects.create(
        project=project,
        prompt="test",
        input_text_hash="old-hash",
        response_data={"title": "Summary"},
    )

    assert project_needs_summary_refresh(project) is False


@pytest.mark.django_db
@override_settings(PROJECT_SUMMARY_AUTO_REFRESH_MAX_AGE_MINUTES=720)
def test_project_needs_summary_refresh_when_cache_is_fresh(project_factory):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    ProjectSummary.objects.create(
        project=project,
        prompt="test",
        input_text_hash="current-hash",
        response_data={"title": "Summary"},
    )

    assert project_needs_summary_refresh(project) is False


@pytest.mark.django_db
@override_settings(
    PROJECT_SUMMARY_AUTO_REFRESH_MAX_AGE_MINUTES=720,
    PROJECT_SUMMARY_AUTO_REFRESH_MAX_PROJECTS_PER_RUN=0,
)
@patch("apps.summarization.project_summary.project_needs_summary_refresh")
def test_get_projects_due_for_summary_refresh_filters_by_ai_flag(
    needs_refresh_mock, project_factory
):
    enabled_org = OrganisationFactory(enable_ai_summarisation=True)
    disabled_org = OrganisationFactory(enable_ai_summarisation=False)
    enabled_project = project_factory(organisation=enabled_org)
    disabled_project = project_factory(organisation=disabled_org)

    def needs_refresh_side_effect(project):
        return project.pk == enabled_project.pk

    needs_refresh_mock.side_effect = needs_refresh_side_effect

    due_projects = get_projects_due_for_summary_refresh()

    assert due_projects == [enabled_project]
    assert disabled_project not in due_projects


@pytest.mark.django_db
@patch("apps.summarization.tasks.generate_project_summary")
def test_refresh_project_summary_skips_org_without_ai_flag(
    generate_mock, project_factory
):
    project = project_factory()

    refresh_project_summary(project.pk)

    generate_mock.assert_not_called()


@pytest.mark.django_db
@override_settings(PROJECT_SUMMARY_AUTO_REFRESH_MAX_AGE_MINUTES=720)
@patch("apps.summarization.tasks.generate_project_summary")
def test_refresh_project_summary_generates_for_enabled_org(
    generate_mock, project_factory
):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)

    refresh_project_summary(project.pk)

    generate_mock.assert_called_once()
    (called_project,) = generate_mock.call_args.args
    assert called_project.pk == project.pk
    assert generate_mock.call_args.kwargs == {"allow_regeneration": True}


@pytest.mark.django_db
@patch("apps.summarization.tasks.refresh_project_summary.delay")
@patch(
    "apps.summarization.tasks.get_projects_due_for_summary_refresh",
    autospec=True,
)
def test_refresh_project_summaries_enqueues_due_projects(
    due_projects_mock, delay_mock, project_factory
):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)
    due_projects_mock.return_value = [project]

    refresh_project_summaries()

    delay_mock.assert_called_once_with(project.pk)
