import pytest
from dateutil.parser import parse
from django.urls import reverse
from freezegun import freeze_time

from apps.ideas import phases as ideas_phases
from apps.projects.timeline import phase_duration_label
from apps.projects.timeline import phase_participation_status


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
