from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from adhocracy4.emails.mixins import SyncEmailMixin
from adhocracy4.projects.models import Project

from apps.projects import emails
from apps.projects.models import ParticipantInvite

User = get_user_model()


class SyncInviteParticipantEmail(SyncEmailMixin, emails.InviteParticipantEmail):
    """Send participant invite emails synchronously (bypasses Celery)."""


class Command(BaseCommand):
    help = (
        "Resend participant invitation emails for pending invites where "
        "no user account exists yet."
    )

    def add_arguments(self, parser):
        target = parser.add_mutually_exclusive_group(required=True)
        target.add_argument(
            "--project-id",
            type=int,
            help="Primary key of the project.",
        )
        target.add_argument(
            "--project-slug",
            help="Project slug (requires --organisation-slug).",
        )
        parser.add_argument(
            "--organisation-slug",
            help="Organisation slug (used with --project-slug).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List matching invites without sending email.",
        )

    def handle(self, *args, **options):
        project = self._get_project(options)
        invites = self._unregistered_pending_invites(project)

        if not invites:
            self.stdout.write(
                self.style.WARNING(
                    f'No pending participant invites without accounts for "{project.name}".'
                )
            )
            return

        self.stdout.write(
            f'Project: {project.name} (id={project.pk}, '
            f'organisation={project.organisation.slug})'
        )
        self.stdout.write(f"Pending unregistered invites: {len(invites)}")

        for invite in invites:
            if options["dry_run"]:
                self.stdout.write(f"  [dry-run] would send to {invite.email}")
                continue

            SyncInviteParticipantEmail().dispatch(invite)
            self.stdout.write(self.style.SUCCESS(f"  sent to {invite.email}"))

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run — no emails sent."))

    def _get_project(self, options):
        project_id = options.get("project_id")
        project_slug = options.get("project_slug")
        organisation_slug = options.get("organisation_slug")

        if project_id is not None:
            project = Project.objects.filter(pk=project_id).first()
            if project is None:
                raise CommandError(f'No project with id={project_id}.')
            return project

        if not organisation_slug:
            raise CommandError(
                "--organisation-slug is required when using --project-slug."
            )

        project = Project.objects.filter(
            slug=project_slug,
            organisation__slug=organisation_slug,
        ).first()
        if project is None:
            raise CommandError(
                f'No project "{project_slug}" in organisation "{organisation_slug}".'
            )
        return project

    def _unregistered_pending_invites(self, project):
        invites = ParticipantInvite.objects.filter(project=project).order_by("email")
        return [
            invite
            for invite in invites
            if not User.objects.filter(email__iexact=invite.email).exists()
        ]
