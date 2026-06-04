import pytest
from dateutil.parser import parse
from django.urls import reverse
from freezegun import freeze_time

from adhocracy4.polls import phases
from apps.projects.timeline import STATUS_FINISHED
from apps.projects.timeline import STATUS_RUNNING
from apps.projects.timeline import STATUS_UPCOMING
from apps.projects.timeline import build_participation_grid_modules
from apps.projects.timeline import build_participation_timeline_groups
from apps.projects.timeline import module_cta_label
from apps.projects.timeline import module_date_range
from apps.projects.timeline import module_participation_status


def project_detail_url(project):
    return reverse(
        "project-detail",
        kwargs={
            "slug": project.slug,
            "organisation_slug": project.organisation.slug,
        },
    )


@pytest.mark.django_db
def test_build_timeline_groups_empty_project(project):
    assert build_participation_timeline_groups(project) == []


@pytest.mark.django_db
def test_build_grid_modules_uses_published_modules(project, module_factory):
    module = module_factory(project=project)
    assert list(build_participation_grid_modules(project)) == [module]


@pytest.mark.django_db
def test_build_timeline_groups_orders_by_start_date(
    project, module_factory, phase_factory
):
    module_past = module_factory(project=project, weight=1)
    module_running = module_factory(project=project, weight=2)
    module_future = module_factory(project=project, weight=3)
    phase_factory(
        module=module_past,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 17:30:00 UTC"),
    )
    phase_factory(
        module=module_running,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )
    phase_factory(
        module=module_future,
        start_date=parse("2013-02-01 17:00:00 UTC"),
        end_date=parse("2013-02-01 19:00:00 UTC"),
    )

    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        groups = build_participation_timeline_groups(project)

    assert len(groups) == 3
    assert groups[0].status == STATUS_FINISHED
    assert groups[0].modules[0] == module_past
    assert groups[1].status == STATUS_RUNNING
    assert groups[1].modules[0] == module_running
    assert groups[2].status == STATUS_UPCOMING
    assert groups[2].modules[0] == module_future


@pytest.mark.django_db
def test_build_timeline_groups_same_day_and_status(
    project, module_factory, phase_factory
):
    module_a = module_factory(project=project, weight=1)
    module_b = module_factory(project=project, weight=2)
    for module in (module_a, module_b):
        phase_factory(
            module=module,
            start_date=parse("2013-01-01 17:00:00 UTC"),
            end_date=parse("2013-01-01 19:00:00 UTC"),
        )

    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        groups = build_participation_timeline_groups(project)

    assert len(groups) == 1
    assert groups[0].status == STATUS_RUNNING
    assert set(groups[0].modules) == {module_a, module_b}


@pytest.mark.django_db
def test_build_timeline_groups_orders_by_status_before_date(
    project, module_factory, phase_factory
):
    """Running modules appear after all past groups even with an earlier start date."""
    module_finished = module_factory(project=project, weight=1)
    module_running = module_factory(project=project, weight=2)
    phase_factory(
        module=module_finished,
        start_date=parse("2013-01-01 10:00:00 UTC"),
        end_date=parse("2013-03-01 12:00:00 UTC"),
    )
    phase_factory(
        module=module_running,
        start_date=parse("2013-02-01 10:00:00 UTC"),
        end_date=parse("2013-12-01 12:00:00 UTC"),
    )

    with freeze_time(parse("2013-04-15 12:00:00 UTC")):
        groups = build_participation_timeline_groups(project)

    assert len(groups) == 2
    assert groups[0].status == STATUS_FINISHED
    assert groups[0].modules[0] == module_finished
    assert groups[1].status == STATUS_RUNNING
    assert groups[1].modules[0] == module_running


@pytest.mark.django_db
def test_build_timeline_groups_same_day_different_status(
    project, module_factory, phase_factory
):
    module_finished = module_factory(project=project, weight=1)
    module_running = module_factory(project=project, weight=2)
    phase_factory(
        module=module_finished,
        start_date=parse("2013-04-10 10:00:00 UTC"),
        end_date=parse("2013-04-10 12:00:00 UTC"),
    )
    phase_factory(
        module=module_running,
        start_date=parse("2013-04-10 14:00:00 UTC"),
        end_date=parse("2013-04-20 12:00:00 UTC"),
    )

    with freeze_time(parse("2013-04-15 12:00:00 UTC")):
        groups = build_participation_timeline_groups(project)

    assert len(groups) == 2
    assert groups[0].group_date.day == 10
    assert groups[0].status == STATUS_FINISHED
    assert groups[1].status == STATUS_RUNNING


@pytest.mark.django_db
def test_module_participation_status_labels(project, module_factory, phase_factory):
    module = module_factory(project=project)
    phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        status, label = module_participation_status(module)
        assert status == STATUS_RUNNING
        assert str(label) == "Running"
        assert str(module_cta_label(module)) == "Participate"
        assert module_date_range(module)


@pytest.mark.django_db
def test_project_detail_includes_participation_views(
    client, project, module_factory, phase_factory, poll_factory
):
    module = module_factory(project=project)
    poll_factory(module=module)
    phase_factory(
        module=module,
        phase_content=phases.VotingPhase(),
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )

    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        response = client.get(project_detail_url(project))

    assert b"data-participation-view" in response.content
    assert b"project-detail-participation-grid" in response.content
    assert b"project-detail-participation-timeline" in response.content
    assert response.context_data["participation_grid_modules"][0] == module
    groups = response.context_data["participation_timeline_groups"]
    assert len(groups) == 1
    assert groups[0].modules[0] == module
