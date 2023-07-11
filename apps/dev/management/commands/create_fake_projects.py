from django.core.management.base import BaseCommand

from apps.users.models import User

user_prefix = "fake_user"
seed = 123
n_projects = 2
n_users = 2
n_comments = 10
n_ratings = 90


class Command(BaseCommand):
    help = "Creates fake projects and user activity"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            default=False,
            help="remove all fake data",
        )

    def handle(self, *args, **options):
        self.clean()
        if options["clean"]:
            return

        """
        organisation = Organisation(name="fake_organisation")
        organisation.save()
        print(organisation)
        """

        for i in range(n_users):
            username = f"{user_prefix}{i:03}"
            u = User(username=username, email=f"{username}@liqd.net")
            u.save()
            print(u)

        print("done")

    def clean(self):
        """
        deleted, _rows_count = Organisation.objects.filter(name="fake_organisation").delete()
        print(f"deleted organisation: {_rows_count}")
        """

        deleted, _rows_count = User.objects.filter(
            username__startswith=user_prefix
        ).delete()
        print(f"deleted users: {_rows_count}")
