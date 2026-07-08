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
from apps.projects.timeline import offline_event_cta_label
from apps.projects.timeline import offline_event_participation_status
from tests.offlineevents.factories import OfflineEventFactory


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
def test_build_grid_modules_orders_like_timeline(
    project, module_factory, phase_factory
):
    module_finished = module_factory(project=project, weight=3)
    module_running = module_factory(project=project, weight=2)
    module_future = module_factory(project=project, weight=1)
    phase_factory(
        module=module_finished,
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
        assert build_participation_grid_modules(project) == [
            module_finished,
            module_running,
            module_future,
        ]


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
    assert groups[0].items[0].module == module_past
    assert groups[1].status == STATUS_RUNNING
    assert groups[1].items[0].module == module_running
    assert groups[2].status == STATUS_UPCOMING
    assert groups[2].items[0].module == module_future


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
    assert {item.module for item in groups[0].items} == {module_a, module_b}


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
    assert groups[0].items[0].module == module_finished
    assert groups[1].status == STATUS_RUNNING
    assert groups[1].items[0].module == module_running


@pytest.mark.django_db
def test_build_timeline_groups_same_status_different_dates(
    project, module_factory, phase_factory
):
    module_early = module_factory(project=project, weight=1)
    module_late = module_factory(project=project, weight=2)
    phase_factory(
        module=module_early,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-03-01 19:00:00 UTC"),
    )
    phase_factory(
        module=module_late,
        start_date=parse("2013-02-01 17:00:00 UTC"),
        end_date=parse("2013-03-01 19:00:00 UTC"),
    )

    with freeze_time(parse("2013-02-15 18:00:00 UTC")):
        groups = build_participation_timeline_groups(project)

    assert len(groups) == 1
    assert groups[0].status == STATUS_RUNNING
    assert tuple(item.module for item in groups[0].items) == (
        module_early,
        module_late,
    )
    assert groups[0].group_date == groups[0].items[0].module.module_start.date()


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
def test_module_cta_label_finished(project, module_factory, phase_factory):
    module = module_factory(project=project)
    phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-02 18:00:00 UTC")):
        assert str(module_cta_label(module)) == "See contributions"


@pytest.mark.django_db
def test_module_cta_label_upcoming(project, module_factory, phase_factory):
    module = module_factory(project=project)
    phase_factory(
        module=module,
        start_date=parse("2013-02-01 17:00:00 UTC"),
        end_date=parse("2013-02-01 19:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        assert str(module_cta_label(module)) == "Read"


@pytest.mark.django_db
def test_build_timeline_groups_includes_offline_events(
    project, module_factory, phase_factory
):
    module = module_factory(project=project)
    phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )
    past_event = OfflineEventFactory(
        project=project,
        name="Past workshop",
        date=parse("2012-12-01 12:00:00 UTC"),
    )
    future_event = OfflineEventFactory(
        project=project,
        name="Future workshop",
        date=parse("2013-03-01 12:00:00 UTC"),
    )

    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        groups = build_participation_timeline_groups(project)

    assert len(groups) == 3
    finished_items = groups[0].items
    assert any(item.offline_event == past_event for item in finished_items)
    running_items = groups[1].items
    assert any(item.module == module for item in running_items)
    upcoming_items = groups[2].items
    assert any(item.offline_event == future_event for item in upcoming_items)


@pytest.mark.django_db
def test_offline_event_participation_status_and_cta(project):
    past_event = OfflineEventFactory(
        project=project,
        date=parse("2012-12-01 12:00:00 UTC"),
    )
    future_event = OfflineEventFactory(
        project=project,
        date=parse("2013-03-01 12:00:00 UTC"),
    )

    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        past_status, _ = offline_event_participation_status(past_event)
        future_status, _ = offline_event_participation_status(future_event)
        assert past_status == STATUS_FINISHED
        assert future_status == STATUS_UPCOMING
        assert str(offline_event_cta_label(past_event)) == "Read"
        assert str(offline_event_cta_label(future_event)) == "Read"


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
    assert groups[0].items[0].module == module
    assert b"project-detail__view-btn-icon" in response.content
    assert b'viewBox="0 0 14.4 12"' in response.content
    assert b"See contributions" not in response.content
    assert b"Participate" in response.content


@pytest.mark.django_db
def test_project_detail_offline_event_links_use_timeline_slide(
    client, project, module_factory, phase_factory
):
    module = module_factory(project=project)
    phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )
    past_event = OfflineEventFactory(
        project=project,
        name="Past workshop",
        date=parse("2012-12-01 12:00:00 UTC"),
    )
    future_event = OfflineEventFactory(
        project=project,
        name="Future workshop",
        date=parse("2013-03-01 12:00:00 UTC"),
    )

    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        response = client.get(project_detail_url(project))

    assert past_event.get_absolute_url().encode() in response.content
    assert future_event.get_absolute_url().encode() in response.content
    assert b"/offlineevents/" in response.content


@pytest.mark.django_db
def test_project_detail_events_section_has_timeline_toggle_attr(
    client, project, module_factory, phase_factory
):
    module = module_factory(project=project)
    phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )
    OfflineEventFactory(project=project, date=parse("2013-03-01 12:00:00 UTC"))

    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        response = client.get(project_detail_url(project))

    assert b"data-participation-events" in response.content
