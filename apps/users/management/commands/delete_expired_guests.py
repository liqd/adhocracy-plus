from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from adhocracy4.comments.models import Comment
from adhocracy4.modules.models import Item
from adhocracy4.polls.models import Answer
from adhocracy4.polls.models import Vote
from adhocracy4.ratings.models import Rating

DEFAULT_MAX_AGE_DAYS = 14


class Command(BaseCommand):
    help = (
        "Delete guest users older than the given age (default 14 days) that have "
        "not created any participation content (ideas/proposals/topics, comments, "
        "poll votes and answers, ratings). Guests with contributions are kept. "
        "Intended to be run once a day (e.g. next to clearsessions)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=DEFAULT_MAX_AGE_DAYS,
            help=(
                "Minimum age in days before an empty guest account is deleted "
                f"(default: {DEFAULT_MAX_AGE_DAYS})."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be deleted without deleting anything.",
        )

    def _has_contributions(self, user):
        """True if the guest created any participation content.

        Neutral ratings (value 0) do not count as a contribution.
        """
        return (
            Item.objects.filter(creator=user).exists()
            or Comment.objects.filter(creator=user).exists()
            or Vote.objects.filter(creator=user).exists()
            or Answer.objects.filter(creator=user).exists()
            or Rating.objects.filter(creator=user).exclude(value=0).exists()
        )

    def handle(self, *args, **options):
        try:
            from guest_user.functions import get_guest_model
        except ImportError:
            self.stdout.write("django-guest-user is not installed; nothing to do.")
            return

        days = options["days"]
        dry_run = options["dry_run"]
        cutoff = timezone.now() - timedelta(days=days)

        guest_model = get_guest_model()
        expired = guest_model.objects.filter(created_at__lt=cutoff).select_related(
            "user"
        )

        deleted = 0
        kept = 0
        for guest in expired:
            user = guest.user
            if self._has_contributions(user):
                kept += 1
                continue
            if dry_run:
                self.stdout.write(f"[dry-run] would delete guest {user.pk} ({user})")
            else:
                # OneToOne(on_delete=CASCADE) removes the Guest row with the user.
                user.delete()
            deleted += 1

        verb = "Would delete" if dry_run else "Deleted"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} {deleted} expired guest(s) with no contributions; "
                f"kept {kept} with contributions (age >= {days}d)."
            )
        )
