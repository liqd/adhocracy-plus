import pytest
from django.core import mail
from django.core.management import call_command

from apps.projects.models import ParticipantInvite


@pytest.mark.django_db
def test_resend_participant_invites_dry_run(
    project_factory, participant_invite_factory, user_factory
):
    project = project_factory()
    participant_invite_factory(
        project=project, email="pending@example.org", site="example.com"
    )
    user_factory(email="registered@example.org")
    participant_invite_factory(
        project=project, email="registered@example.org", site="example.com"
    )

    mail.outbox.clear()
    call_command(
        "resend_participant_invites",
        "--project-id",
        str(project.pk),
        "--dry-run",
    )

    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_resend_participant_invites_sends_to_unregistered_only(
    project_factory, participant_invite_factory, user_factory
):
    project = project_factory()
    participant_invite_factory(
        project=project, email="pending@example.org", site="example.com"
    )
    user_factory(email="registered@example.org")
    participant_invite_factory(
        project=project, email="registered@example.org", site="example.com"
    )

    mail.outbox.clear()
    call_command("resend_participant_invites", "--project-id", str(project.pk))

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["pending@example.org"]
    assert ParticipantInvite.objects.filter(project=project).count() == 2
