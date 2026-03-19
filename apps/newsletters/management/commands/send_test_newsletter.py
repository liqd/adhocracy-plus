from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from adhocracy4.emails.mixins import SyncEmailMixin
from apps.newsletters import emails
from apps.newsletters import models

User = get_user_model()


class SyncNewsletterEmail(SyncEmailMixin, emails.NewsletterEmail):
    """Synchronous newsletter sending (bypasses Celery)."""


class SyncDirectNewsletterEmail(SyncEmailMixin, emails.NewsletterEmail):
    """Send to explicitly provided receivers, bypassing newsletter preferences."""

    def get_receivers(self):
        return self.kwargs["receivers_override"]


class Command(BaseCommand):
    help = "Send a newsletter email synchronously to a single user."

    def add_arguments(self, parser):
        parser.add_argument("email", help="Receiver email address")
        parser.add_argument("--subject", default="Test newsletter")
        parser.add_argument("--body", default="Hello – this is a test newsletter.")
        parser.add_argument("--sender", default="test@example.org")
        parser.add_argument("--sender-name", default="Test")
        parser.add_argument(
            "--organisation-pk",
            type=int,
            default=None,
            help="Optional organisation pk (used for branding / reply-to context)",
        )
        parser.add_argument(
            "--ignore-preferences",
            action="store_true",
            help="Send even if the user opted out of newsletters (get_newsletters=False).",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Print diagnostic information (settings, receiver selection, counts).",
        )

    def handle(self, *args, **options):
        receiver_email = options["email"]
        user = User.objects.filter(email=receiver_email).first()
        organisation_pk = options["organisation_pk"]

        if options["debug"]:
            self.stdout.write("== Newsletter test diagnostics ==")
            self.stdout.write(f"DJANGO_SETTINGS_MODULE={getattr(settings, 'SETTINGS_MODULE', None)}")
            self.stdout.write(f"EMAIL_BACKEND={getattr(settings, 'EMAIL_BACKEND', None)}")
            self.stdout.write(
                f"CELERY_TASK_ALWAYS_EAGER={getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', None)}"
            )
            self.stdout.write(f"receiver_email={receiver_email}")
            if user:
                self.stdout.write(f"user_id={user.id}")
                self.stdout.write(f"user_is_active={user.is_active}")
                self.stdout.write(
                    f"user_get_newsletters={getattr(user, 'get_newsletters', None)}"
                )
            else:
                self.stdout.write("user_id=<not found>")

        nl = models.Newsletter.objects.create(
            creator=user,
            sender_name=options["sender_name"],
            sender=options["sender"],
            subject=options["subject"],
            body=options["body"],
            receivers=models.PROJECT,
            organisation_id=organisation_pk,
            sent=timezone.now(),
        )

        if not user:
            self.stdout.write(
                "No matching user found; sending directly to email address."
            )
            mails = SyncDirectNewsletterEmail.send(
                nl,
                receivers_override=[receiver_email],
                organisation_pk=organisation_pk,
            )
            if options["debug"]:
                self.stdout.write(f"direct_receivers=1")
                self.stdout.write(f"sent_mails={len(mails)}")
            return

        if options["ignore_preferences"]:
            self.stdout.write(
                "Sending directly (ignoring newsletter preferences) to existing user."
            )
            mails = SyncDirectNewsletterEmail.send(
                nl,
                receivers_override=[user],
                organisation_pk=organisation_pk,
            )
            if options["debug"]:
                self.stdout.write("mode=direct(ignore-preferences)")
                self.stdout.write("direct_receivers=1")
                self.stdout.write(f"sent_mails={len(mails)}")
            return

        if options["debug"]:
            qs = (
                User.objects.filter(id__in=[user.id])
                .filter(get_newsletters=True)
                .filter(is_active=True)
                .distinct()
            )
            self.stdout.write("mode=filtered(get_newsletters & is_active)")
            self.stdout.write(f"participant_ids=[{user.id}]")
            self.stdout.write(f"filtered_receivers={qs.count()}")

        mails = SyncNewsletterEmail.send(
            nl,
            participant_ids=[user.id],
            organisation_pk=organisation_pk,
        )
        self.stdout.write(f"Dispatched {len(mails)} email(s).")

