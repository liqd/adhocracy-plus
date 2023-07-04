from datetime import timedelta

import pytest
from dateutil.parser import parse
from django.core import mail
from django.core.management import call_command
from freezegun import freeze_time


@pytest.mark.django_db
def test_notify_follower_on_phase_started(phase_factory):
    phase = phase_factory(
        start_date=parse("2022-01-01 17:00:00 UTC"),
        end_date=parse("2022-05-01 18:00:00 UTC"),
    )

    with freeze_time(phase.start_date + timedelta(minutes=30)):
        call_command("create_system_actions")

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject.startswith("Here we go:")


@pytest.mark.django_db
def test_notify_follower_on_phase_over_soon(phase_factory):
    phase = phase_factory(
        start_date=parse("2022-01-01 17:00:00 UTC"),
        end_date=parse("2022-05-01 18:00:00 UTC"),
    )

    with freeze_time(phase.end_date - timedelta(minutes=30)):
        call_command("create_system_actions")

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject.startswith("Participation ends soon for")


@pytest.mark.django_db
def test_notify_follower_on_upcoming_event(offline_event_factory):
    offline_event = offline_event_factory(
        date=parse("2022-01-05 17:00:00 UTC"),
    )

    with freeze_time(offline_event.date - timedelta(minutes=30)):
        call_command("create_offlineevent_system_actions")

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject.startswith("Event in project ")
