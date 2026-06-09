from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from adhocracy4.projects.models import Project
from apps.projects.publish_results_reminder import SKIP_REASON_LABELS
from apps.projects.publish_results_reminder import send_publish_results_reminder


class Command(BaseCommand):
    help = (
        "Send the publish-results reminder email to every initiator of the project's "
        "organisation (one message per initiator). Uses the same eligibility rules "
        "as automatic sending unless --force is passed."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "project_slug",
            help="Project slug as in the project URL path.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help=(
                "Send even when the project is not eligible (skips all checks and "
                "does not update results_reminder_sent_at)."
            ),
        )

    def handle(self, *args, **options):
        slug = options["project_slug"]
        force = options["force"]
        try:
            project = Project.objects.select_related("organisation", "insight").get(
                slug=slug
            )
        except Project.DoesNotExist as exc:
            raise CommandError(f'No project with slug "{slug}".') from exc

        skip_reason = send_publish_results_reminder(project, force=force)
        if skip_reason:
            label = SKIP_REASON_LABELS.get(skip_reason, skip_reason)
            raise CommandError(
                f'Project "{slug}" is not eligible for a publish-results reminder: '
                f"{label}."
            )

        n_initiators = project.organisation.initiators.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Publish-results reminder sent for project {slug!r}: "
                f"{n_initiators} e-mail(s), one per initiator of the organisation."
            )
        )
