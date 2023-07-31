import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from adhocracy4.comments.models import Comment
from adhocracy4.modules.models import Module
from adhocracy4.phases.models import Phase
from adhocracy4.ratings.models import Rating
from apps.ideas.models import Idea
from apps.organisations.models import Member
from apps.organisations.models import Organisation
from apps.projects.models import Project
from apps.users.models import User


class Command(BaseCommand):
    help = """
    Creates fake projects and user activity.

    Currently only implements brain storming modules with parameters for
    number of users, ideas, comments and ratings.

    The command on its own counts and lists fake data.
    The argument --clean removes all fake data.
    The argument --re-create first removes and then re-creates fake data.

    Usage:

        $ ./manage.py create_fake_projects
        $ ./manage.py create_fake_projects --clean
        $ ./manage.py create_fake_projects --re-create
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--clean",
            action="store_true",
            default=False,
            help="remove all fake data",
        )
        parser.add_argument(
            "--re-create",
            action="store_true",
            default=False,
            help="remove and re-create all fake data",
        )
        parser.add_argument(
            "--admin",
            action="store_true",
            default="admin@liqd.net",
            help="admin email to add to organisation",
        )

    def handle(self, *args, **options):
        n_projects = 1
        n_users = 10
        n_ideas = 1
        n_comments = 100
        n_ratings = 1

        if options["clean"]:
            remove_fake_data()
            return

        list_fake_data()

        if not options["re_create"]:
            return

        seed = None
        if seed:
            random.seed(seed)

        remove_fake_data()
        now = timezone.now()
        start_time = now - timedelta(days=10)
        end_time = now + timedelta(days=10)

        email = options["admin"]
        admin = User.objects.filter(email=email).first()

        if not admin:
            known = sorted(User.objects.values_list("email", flat=True))
            print(f"unknown user email: {email=}, {known=}")
            return

        organisation = Organisation(name="fake_organisation")
        organisation.save()
        organisation.initiators.add(admin.id)

        member = Member(
            member=admin,
            organisation=organisation,
        )
        member.save()

        users = create_users(n=n_users)

        for i in range(n_projects):
            project = Project(
                name=f"fake_project_{i:03}",
                organisation=organisation,
                description="fake_description",
                information="fake_information",
                is_draft=False,
            )
            project.save()
            project.moderators.add(admin)

            create_brainstorming_module(
                n_ideas=n_ideas,
                n_comments=n_comments,
                n_ratings=n_ratings,
                project=project,
                users=users,
                start_time=start_time,
                end_time=end_time,
            )

        print("done")


def create_users(n):
    users = []

    for i in range(n):
        username = f"fake_user_{i:03}"
        user = User(username=username, email=f"{username}@liqd.net")
        users.append(user)

    User.objects.bulk_create(users)
    users = list(User.objects.filter(username__startswith="fake_"))

    print(f"created users: {len(users)=}")

    return users


def create_brainstorming_module(
    n_ideas,
    n_comments,
    n_ratings,
    project,
    users,
    start_time,
    end_time,
):
    module = Module(
        name="fake_brainstorming",
        description="fake_description",
        project=project,
        weight=1,
        is_draft=False,
    )
    module.save()

    phase = Phase(
        type="a4_candy_ideas:collect",
        module=module,
        name="fake_phase",
        description="fake_description",
        start_date=start_time,
        end_date=end_time,
    )
    phase.save()

    ideas = []
    for _ in range(n_ideas):
        idea = Idea(
            name="fake_idea",
            module=module,
            creator=random.choice(users),
            description="fake_description",
            slug="fake_slug",
        )
        ideas.append(idea)
        idea.save()

    print(f"created ideas: {len(ideas)=}")

    comments = []
    for _ in range(n_comments):
        comment = Comment(
            comment="fake_comment",
            content_object=random.choice(ideas),
            creator=random.choice(users),
            project=project,
        )
        comments.append(comment)

    Comment.objects.bulk_create(comments)
    comments = list(Comment.objects.filter(comment="fake_comment"))

    print(f"created comments: {len(comments)=}")

    k = min(n_ratings, len(users), n_ideas)
    zipped = zip(
        random.sample(population=users, k=k),
        random.sample(population=ideas, k=k),
    )

    ratings = []
    for user, idea in zipped:
        rating = Rating(
            content_object=idea,
            value=random.choice([-1, 1]),
            creator=random.choice(users),
        )
        ratings.append(rating)

    Rating.objects.bulk_create(objs=ratings)

    print(f"created ratings: {len(ratings)=}")

    return module, ideas, comments, ratings


def list_fake_data():
    models = [
        (Organisation, "name"),
        (Project, "name"),
        (User, "username"),
        (Project, "name"),
        (Comment, "comment"),
    ]

    for model, key in models:
        count = model.objects.filter(**{f"{key}__startswith": "fake_"}).count()
        print(f"{model.__name__}: {count=}")


def remove_fake_data():
    models = [
        (Organisation, "name"),
        (Project, "name"),
        (User, "username"),
        (Project, "name"),
        (Comment, "comment"),
        (Module, "name"),
    ]

    for model, key in models:
        deleted, _rows_count = model.objects.filter(
            **{f"{key}__startswith": "fake_"},
        ).delete()

        if _rows_count:
            print(f"deleting {model.__name__}: {_rows_count}")
