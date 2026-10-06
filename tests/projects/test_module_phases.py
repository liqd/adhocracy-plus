import pytest
from dateutil.parser import parse
from django.urls import reverse
from freezegun import freeze_time

from apps.ideas import phases as ideas_phases
from apps.projects.timeline import build_phase_timeline
from apps.projects.timeline import phase_completed_label
from apps.projects.timeline import phase_duration_label
from apps.projects.timeline import phase_participation_status
from apps.projects.timeline import phase_progress
from apps.projects.timeline import phase_starts_label
from apps.projects.timeline import phase_time_left_label


@pytest.mark.django_db
def test_phase_participation_status_completed(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 18:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-02 18:00:00 UTC")):
        status, label = phase_participation_status(phase)
    assert status == "completed"


@pytest.mark.django_db
def test_phase_participation_status_active(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        status, label = phase_participation_status(phase)
    assert status == "active"


@pytest.mark.django_db
def test_phase_participation_status_upcoming(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-02-01 17:00:00 UTC"),
        end_date=parse("2013-02-01 19:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        status, label = phase_participation_status(phase)
    assert status == "upcoming"


@pytest.mark.django_db
def test_phase_participation_status_without_end_date(phase_factory, module_factory):
    # Matches a4's Phase.is_over: a phase without an end date is "over",
    # never "active" (so module.active_phase stays None and the badge
    # cannot contradict the "participation is not possible" notice).
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=None,
    )
    with freeze_time(parse("2013-01-03 18:00:00 UTC")):
        status, label = phase_participation_status(phase)
    assert status == "completed"


@pytest.mark.django_db
def test_phase_participation_status_at_end_date(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-05 18:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-05 18:00:00 UTC")):
        status, label = phase_participation_status(phase)
    assert status == "completed"


@pytest.mark.django_db
def test_phase_participation_status_without_start_date(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=None,
        end_date=parse("2013-01-05 18:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-03 18:00:00 UTC")):
        status, label = phase_participation_status(phase)
    assert status == "upcoming"


@pytest.mark.django_db
def test_phase_duration_label_days(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-04 17:00:00 UTC"),
    )
    assert phase_duration_label(phase) == "3 days"


@pytest.mark.django_db
def test_phase_duration_label_weeks(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-22 17:00:00 UTC"),
    )
    assert phase_duration_label(phase) == "3 weeks"


@pytest.mark.django_db
def test_phase_duration_label_months(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-04-01 17:00:00 UTC"),
    )
    assert phase_duration_label(phase) == "3 months"


@pytest.mark.django_db
def test_phase_duration_label_same_day_hours(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 09:00:00 UTC"),
        end_date=parse("2013-01-01 13:00:00 UTC"),
    )
    assert phase_duration_label(phase) == "4 hours"


@pytest.mark.django_db
def test_phase_duration_label_hours_across_midnight(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 23:00:00 UTC"),
        end_date=parse("2013-01-02 01:00:00 UTC"),
    )
    assert phase_duration_label(phase) == "2 hours"


@pytest.mark.django_db
def test_phase_duration_label_minutes(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 10:00:00 UTC"),
        end_date=parse("2013-01-01 10:30:00 UTC"),
    )
    assert phase_duration_label(phase) == "30 minutes"


@pytest.mark.django_db
def test_phase_duration_label_empty_without_end(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=None,
    )
    assert phase_duration_label(phase) == ""


def _phase_for_module(phase_factory, module, weight, start, end, name):
    content = ideas_phases.CollectPhase()
    return phase_factory(
        module=module,
        weight=weight,
        phase_content=content,
        name=name,
        start_date=parse(start),
        end_date=parse(end),
    )


@pytest.mark.django_db
def test_phase_progress_midpoint(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 00:00:00 UTC"),
        end_date=parse("2013-01-11 00:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-06 00:00:00 UTC")):
        assert phase_progress(phase) == 50


@pytest.mark.django_db
def test_phase_progress_is_none_outside_window(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 00:00:00 UTC"),
        end_date=parse("2013-01-11 00:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-20 00:00:00 UTC")):
        assert phase_progress(phase) is None


@pytest.mark.django_db
def test_phase_progress_clamped_at_bounds(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 00:00:00 UTC"),
        end_date=parse("2013-01-11 00:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-01 00:00:00 UTC")):
        assert phase_progress(phase) == 0
    with freeze_time(parse("2013-01-10 23:59:59 UTC")):
        assert phase_progress(phase) == 100


@pytest.mark.django_db
def test_phase_time_left_label_days(phase_factory, module_factory):
    module = module_factory()
    phase = phase_factory(
        module=module,
        start_date=parse("2013-01-01 00:00:00 UTC"),
        end_date=parse("2013-01-04 00:00:00 UTC"),
    )
    with freeze_time(parse("2013-01-01 00:00:00 UTC")):
        assert phase_time_left_label(phase) == "3 days left"


@pytest.mark.django_db
def test_phase_completed_and_starts_labels(phase_factory, module_factory):
    module = module_factory()
    completed = phase_factory(
        module=module,
        start_date=parse("2013-01-01 00:00:00 UTC"),
        end_date=parse("2013-01-02 00:00:00 UTC"),
    )
    upcoming = phase_factory(
        module=module,
        start_date=parse("2013-02-20 00:00:00 UTC"),
        end_date=parse("2013-02-22 00:00:00 UTC"),
    )
    assert phase_completed_label(completed) == "Completed on Jan. 2, 2013"
    assert phase_starts_label(upcoming) == "Starts on Feb. 20, 2013"


@pytest.mark.django_db
def test_build_phase_timeline_hidden_before_start(phase_factory, module_factory):
    module = module_factory()
    _phase_for_module(
        phase_factory,
        module,
        0,
        "2013-02-01 17:00:00 UTC",
        "2013-02-05 17:00:00 UTC",
        "Collect ideas",
    )
    with freeze_time(parse("2013-01-01 00:00:00 UTC")):
        timeline = build_phase_timeline(module)
    assert timeline.is_visible is False
    assert all(not step.is_current for step in timeline.steps)


@pytest.mark.django_db
def test_build_phase_timeline_current_active(phase_factory, module_factory):
    module = module_factory()
    _phase_for_module(
        phase_factory,
        module,
        0,
        "2013-01-01 17:00:00 UTC",
        "2013-01-01 18:00:00 UTC",
        "Collect ideas",
    )
    _phase_for_module(
        phase_factory,
        module,
        1,
        "2013-01-02 17:00:00 UTC",
        "2013-01-05 18:00:00 UTC",
        "Discuss",
    )
    _phase_for_module(
        phase_factory,
        module,
        2,
        "2013-01-10 17:00:00 UTC",
        "2013-01-12 18:00:00 UTC",
        "Vote",
    )
    with freeze_time(parse("2013-01-03 18:00:00 UTC")):
        timeline = build_phase_timeline(module)
    assert timeline.is_visible is True
    current = [step for step in timeline.steps if step.is_current]
    assert len(current) == 1
    assert current[0].phase.name == "Discuss"
    assert current[0].status == "active"
    assert current[0].progress is not None
    assert current[0].detail_label == "2 days left"

    by_name = {step.phase.name: step for step in timeline.steps}
    assert by_name["Collect ideas"].progress == 100
    assert by_name["Collect ideas"].detail_label.startswith("Completed on")
    assert by_name["Vote"].progress == 0
    assert by_name["Vote"].detail_label.startswith("Starts on")


@pytest.mark.django_db
def test_build_phase_timeline_between_phases_shows_upcoming(
    phase_factory, module_factory
):
    module = module_factory()
    _phase_for_module(
        phase_factory,
        module,
        0,
        "2013-01-01 17:00:00 UTC",
        "2013-01-01 18:00:00 UTC",
        "Collect ideas",
    )
    _phase_for_module(
        phase_factory,
        module,
        1,
        "2013-02-01 17:00:00 UTC",
        "2013-02-05 18:00:00 UTC",
        "Vote",
    )
    with freeze_time(parse("2013-01-03 18:00:00 UTC")):
        timeline = build_phase_timeline(module)
    assert timeline.is_visible is True
    current = [step for step in timeline.steps if step.is_current]
    assert len(current) == 1
    assert current[0].phase.name == "Vote"
    assert current[0].status == "upcoming"
    assert current[0].progress == 0
    assert current[0].detail_label.startswith("Starts on")

    completed = [step for step in timeline.steps if step.status == "completed"]
    assert completed[0].progress == 100
    assert completed[0].detail_label.startswith("Completed on")


@pytest.mark.django_db
def test_build_phase_timeline_finished_shows_last_completed(
    phase_factory, module_factory
):
    module = module_factory()
    _phase_for_module(
        phase_factory,
        module,
        0,
        "2013-01-01 17:00:00 UTC",
        "2013-01-01 18:00:00 UTC",
        "Collect ideas",
    )
    _phase_for_module(
        phase_factory,
        module,
        1,
        "2013-01-02 17:00:00 UTC",
        "2013-01-05 18:00:00 UTC",
        "Vote",
    )
    with freeze_time(parse("2013-02-03 18:00:00 UTC")):
        timeline = build_phase_timeline(module)
    assert timeline.is_visible is True
    current = [step for step in timeline.steps if step.is_current]
    assert len(current) == 1
    assert current[0].phase.name == "Vote"
    assert current[0].status == "completed"
    assert current[0].progress == 100
    assert current[0].detail_label.startswith("Completed on")


@pytest.mark.django_db
def test_module_detail_renders_all_phases_with_status(
    client, phase_factory, module_factory, organisation
):
    module = module_factory(project__organisation=organisation)
    completed = _phase_for_module(
        phase_factory,
        module,
        0,
        "2013-01-01 17:00:00 UTC",
        "2013-01-01 18:00:00 UTC",
        "Collect ideas",
    )
    active = _phase_for_module(
        phase_factory,
        module,
        1,
        "2013-01-02 17:00:00 UTC",
        "2013-01-05 18:00:00 UTC",
        "Discuss",
    )
    upcoming = _phase_for_module(
        phase_factory,
        module,
        2,
        "2013-01-10 17:00:00 UTC",
        "2013-01-12 18:00:00 UTC",
        "Vote",
    )

    url = reverse(
        "module-detail",
        kwargs={
            "organisation_slug": organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_time(parse("2013-01-03 18:00:00 UTC")):
        response = client.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    for phase in (completed, active, upcoming):
        assert phase.name in content
    assert "Completed" in content
    assert "Active" in content
    assert "Upcoming" in content
    assert "phase-stepper" in content
    assert content.count("data-phase-progress") == 3


@pytest.mark.django_db
def test_module_detail_hides_timeline_before_start(
    client, phase_factory, module_factory, organisation
):
    module = module_factory(project__organisation=organisation)
    _phase_for_module(
        phase_factory,
        module,
        0,
        "2013-02-01 17:00:00 UTC",
        "2013-02-05 18:00:00 UTC",
        "Collect ideas",
    )

    url = reverse(
        "module-detail",
        kwargs={
            "organisation_slug": organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_time(parse("2013-01-03 18:00:00 UTC")):
        response = client.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    assert "phase-stepper" not in content
    assert "Participation is not possible at the moment." in content


@pytest.mark.django_db
def test_module_detail_shows_completed_date_when_finished(
    client, phase_factory, module_factory, organisation
):
    module = module_factory(project__organisation=organisation)
    _phase_for_module(
        phase_factory,
        module,
        0,
        "2013-01-01 17:00:00 UTC",
        "2013-01-05 18:00:00 UTC",
        "Collect ideas",
    )

    url = reverse(
        "module-detail",
        kwargs={
            "organisation_slug": organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_time(parse("2013-02-03 18:00:00 UTC")):
        response = client.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    assert "phase-stepper" in content
    assert "Completed on" in content
    assert "data-phase-progress" in content
    assert "width: 100%" in content


@pytest.mark.django_db
def test_module_detail_shows_upcoming_bar_while_phase_active(
    client, phase_factory, module_factory, organisation
):
    module = module_factory(project__organisation=organisation)
    _phase_for_module(
        phase_factory,
        module,
        0,
        "2013-01-02 17:00:00 UTC",
        "2013-01-05 18:00:00 UTC",
        "Discuss",
    )
    _phase_for_module(
        phase_factory,
        module,
        1,
        "2013-01-10 17:00:00 UTC",
        "2013-01-12 18:00:00 UTC",
        "Vote",
    )

    url = reverse(
        "module-detail",
        kwargs={
            "organisation_slug": organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_time(parse("2013-01-03 18:00:00 UTC")):
        response = client.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    assert "Starts on" in content
    assert content.count("data-phase-progress") == 2


@pytest.mark.django_db
def test_module_detail_shows_bar_and_start_date_for_upcoming(
    client, phase_factory, module_factory, organisation
):
    module = module_factory(project__organisation=organisation)
    _phase_for_module(
        phase_factory,
        module,
        0,
        "2013-01-01 17:00:00 UTC",
        "2013-01-01 18:00:00 UTC",
        "Collect ideas",
    )
    _phase_for_module(
        phase_factory,
        module,
        1,
        "2013-02-01 17:00:00 UTC",
        "2013-02-05 18:00:00 UTC",
        "Vote",
    )

    url = reverse(
        "module-detail",
        kwargs={
            "organisation_slug": organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_time(parse("2013-01-03 18:00:00 UTC")):
        response = client.get(url)
    assert response.status_code == 200

    content = response.content.decode()
    assert "phase-stepper" in content
    assert "Starts on" in content
    assert "data-phase-progress" in content
