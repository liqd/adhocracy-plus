from datetime import timedelta
from unittest.mock import patch

import pytest
from django.test.utils import override_settings
from django.utils import timezone

from apps.projects.summary_tasks import generate_project_summary_task
from apps.projects.summary_tasks import refresh_project_summaries
from apps.projects.utils import project_needs_summary_refresh
from apps.summarization.models import ProjectSummary
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
def test_refresh_project_summaries_only_enqueues_ai_enabled_orgs(project_factory):
    enabled_org = OrganisationFactory(enable_ai_summarisation=True)
    disabled_org = OrganisationFactory(enable_ai_summarisation=False)
    enabled_project = project_factory(organisation=enabled_org)
    project_factory(organisation=disabled_org)

    with patch(
        "apps.projects.summary_tasks.generate_project_summary_task.delay"
    ) as delay_mock:
        refresh_project_summaries()

    delay_mock.assert_called_once_with(enabled_project.id)


@pytest.mark.django_db
@patch("apps.projects.summary_tasks.generate_project_summary")
def test_generate_project_summary_task_skips_org_without_ai_flag(
    generate_mock, project_factory
):
    project = project_factory()

    generate_project_summary_task(project.pk)

    generate_mock.assert_not_called()


@pytest.mark.django_db
@override_settings(PROJECT_SUMMARY_AUTO_REFRESH_MAX_AGE_MINUTES=720)
@patch("apps.projects.summary_tasks.generate_project_summary")
def test_generate_project_summary_task_generates_for_enabled_org(
    generate_mock, project_factory
):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)

    generate_project_summary_task(project.pk)

    generate_mock.assert_called_once()
    (called_project,) = generate_mock.call_args.args
    assert called_project.pk == project.pk
    assert generate_mock.call_args.kwargs["allow_regeneration"] is True


@pytest.mark.django_db
@patch("apps.projects.summary_tasks.generate_project_summary_task.delay")
def test_refresh_project_summaries_enqueues_stale_projects(delay_mock, project_factory):
    organisation = OrganisationFactory(enable_ai_summarisation=True)
    project = project_factory(organisation=organisation)

    refresh_project_summaries()

    delay_mock.assert_called_once_with(project.id)
