import os
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.newsletters.emails import NewsletterSettingsNoticeEmail

User = get_user_model()

# v2601.1 (2026-01-22) shipped the change that reset the newsletter opt-in
# whenever a user saved their profile. Users who were logged in after that
# date could plausibly have been affected, but only those currently opted out
# are candidates.
BUG_DATE = timezone.make_aware(datetime(2026, 1, 22))

DEFAULT_LOG_FILE = "/var/log/django/newsletter_settings_notice.log"


class Command(BaseCommand):
    help = (
        "Send a one-time notice email to users whose newsletter opt-in may "
        "have been reset by a bug. Recipients are the refined candidate pool: "
        "currently opted out, active, and logged in since the bug shipped. "
        "Guest accounts are excluded. Every recipient is appended to a log "
        "file, so re-runs are idempotent and never send twice."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only print the number of recipients; do not send emails.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Send to at most this many users (useful for staged rollouts). "
            "Sent users are logged and skipped on later runs.",
        )
        parser.add_argument(
            "--to",
            dest="to_email",
            default=None,
            help="Send a single test copy to this email address instead of "
            "the candidate pool (nothing is logged).",
        )
        parser.add_argument(
            "--log-file",
            dest="log_file",
            default=DEFAULT_LOG_FILE,
            help=f"File to append sent recipients to (default: {DEFAULT_LOG_FILE}).",
        )

    def handle(self, *args, **options):
        if options["to_email"]:
            self._send_test_copy(options["to_email"])
            return

        dry_run = options["dry_run"]
        limit = options["limit"]
        log_file = options["log_file"]

        already_sent = self._load_sent_emails(log_file)

        candidates = (
            User.objects.filter(
                get_newsletters=False,
                is_active=True,
                last_login__gte=BUG_DATE,
            )
            .exclude(email__startswith="guest+")
            .exclude(email__in=already_sent)
            .order_by("pk")
        )
        count = candidates.count()
        if limit:
            candidates = candidates[:limit]

        verb = "would send" if dry_run else "sending"
        self.stdout.write(f"{verb} notice email to {count} user(s)")

        if dry_run:
            return

        if count:
            os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)

        sent = 0
        with open(log_file, "a") as log:
            for user in candidates.iterator():
                NewsletterSettingsNoticeEmail(user).dispatch(user)
                log.write(f"{timezone.now():%Y-%m-%d %H:%M:%S} {user.email}\n")
                sent += 1

        self.stdout.write(self.style.SUCCESS(f"done ({sent} sent)"))

    def _load_sent_emails(self, path):
        """Return the set of email addresses already logged as sent."""
        sent = set()
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        sent.add(line.split()[-1])
        return sent

    def _send_test_copy(self, email):
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            self.stderr.write(f"No user with email {email}")
            return
        NewsletterSettingsNoticeEmail(user).dispatch(user)
        self.stdout.write(self.style.SUCCESS(f"test copy sent to {email}"))
