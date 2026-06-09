from datetime import timedelta

import pytest
from django.core import mail
from django.test.utils import override_settings
from django.utils import timezone

from adhocracy4.test.helpers import setup_phase
from apps.ideas.phases import CollectPhase
from apps.projects.models import ProjectInsight
from apps.projects.tasks import send_publish_results_reminders


@pytest.mark.django_db
@override_settings(
    RESULTS_PUBLISH_REMINDER_DELAY_HOURS=0,
    RESULTS_PUBLISH_REMINDER_MIN_LAST_PARTICIPATION_END=None,
)
def test_send_publish_results_reminder_sends_email(phase_factory):
    phase, module, project, _item = setup_phase(phase_factory, None, CollectPhase)
    project.result = ""
    project.save()

    now = timezone.now()
    phase.start_date = now - timedelta(days=5)
    phase.end_date = now - timedelta(hours=2)
    phase.save()

    assert not mail.outbox
    send_publish_results_reminders()
    assert len(mail.outbox) == 1
    subject = mail.outbox[0].subject
    assert "results" in subject.lower() or "Ergebnisse" in subject
    assert project.organisation.initiators.filter(email=mail.outbox[0].to[0]).exists()

    insight = ProjectInsight.objects.get(project=project)
    assert insight.results_reminder_sent_at is not None


@pytest.mark.django_db
@override_settings(
    RESULTS_PUBLISH_REMINDER_DELAY_HOURS=0,
    RESULTS_PUBLISH_REMINDER_MIN_LAST_PARTICIPATION_END=None,
)
def test_send_publish_results_reminder_skips_when_results_present(phase_factory):
    phase, module, project, _item = setup_phase(phase_factory, None, CollectPhase)
    project.result = "<p>Some results</p>"
    project.save()

    now = timezone.now()
    phase.start_date = now - timedelta(days=5)
    phase.end_date = now - timedelta(hours=2)
    phase.save()

    send_publish_results_reminders()
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_send_publish_results_reminder_skips_when_last_end_before_min_cutoff(
    phase_factory,
):
    phase, module, project, _item = setup_phase(phase_factory, None, CollectPhase)
    project.result = ""
    project.save()

    now = timezone.now()
    phase.start_date = now - timedelta(days=5)
    phase.end_date = now - timedelta(hours=2)
    phase.save()

    min_cutoff = now - timedelta(hours=1)
    with override_settings(
        RESULTS_PUBLISH_REMINDER_DELAY_HOURS=0,
        RESULTS_PUBLISH_REMINDER_MIN_LAST_PARTICIPATION_END=min_cutoff,
    ):
        send_publish_results_reminders()
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_send_publish_results_reminder_sends_when_last_end_on_or_after_min_cutoff(
    phase_factory,
):
    phase, module, project, _item = setup_phase(phase_factory, None, CollectPhase)
    project.result = ""
    project.save()

    now = timezone.now()
    phase.start_date = now - timedelta(days=5)
    phase.end_date = now - timedelta(hours=2)
    phase.save()

    min_cutoff = now - timedelta(days=10)
    with override_settings(
        RESULTS_PUBLISH_REMINDER_DELAY_HOURS=0,
        RESULTS_PUBLISH_REMINDER_MIN_LAST_PARTICIPATION_END=min_cutoff,
    ):
        send_publish_results_reminders()
    assert len(mail.outbox) == 1


@pytest.mark.django_db
@override_settings(
    RESULTS_PUBLISH_REMINDER_DELAY_HOURS=168,
    RESULTS_PUBLISH_REMINDER_MIN_LAST_PARTICIPATION_END=None,
)
def test_send_publish_results_reminder_respects_delay(phase_factory):
    phase, module, project, _item = setup_phase(phase_factory, None, CollectPhase)
    project.result = ""
    project.save()

    now = timezone.now()
    phase.start_date = now - timedelta(days=5)
    phase.end_date = now - timedelta(hours=2)
    phase.save()

    send_publish_results_reminders()
    assert len(mail.outbox) == 0
