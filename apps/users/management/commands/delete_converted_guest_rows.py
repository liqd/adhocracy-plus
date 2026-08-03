from django.core.management.base import BaseCommand
from guest_user.models import Guest


class Command(BaseCommand):
    help = (
        "Delete Guest rows belonging to users who have converted to a regular "
        "account (identified by a non-guest email address). A leftover Guest "
        "row makes the platform treat the account as a guest, which excludes "
        "it from notification emails. Only the Guest row is deleted, never "
        "the user."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only show which Guest rows would be deleted.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Guest accounts are created with a guest+<username>@liqd.net
        # placeholder email; a different email means the user converted.
        converted = Guest.objects.exclude(user__email__startswith="guest+")

        count = converted.count()
        for guest in converted.select_related("user"):
            self.stdout.write(
                f"{'[dry-run] would delete' if dry_run else 'deleting'} "
                f"Guest row of user {guest.user.pk} ({guest.user.email})"
            )

        if not dry_run:
            converted.delete()

        verb = "would delete" if dry_run else "deleted"
        self.stdout.write(f"{verb} {count} stale Guest row(s).")
