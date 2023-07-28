from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from apps import logger
from apps.projects.insights import create_insights
from apps.projects.models import Project


class Command(BaseCommand):
    help = "Resets the insights and participation tables."

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--project",
            help="project slug, resets data for this project only",
        )

    def handle(self, *args, **options):
        slug = options["project"]

        if slug:
            project = Project.objects.filter(slug=slug).first()
            if not project:
                known = Project.objects.order_by("slug").values_list("slug", flat=True)
                logger.warning(f"unknown project slug: {slug=}, {list(known)=}")
                return

            projects = [project]
        else:
            projects = Project.objects.all()

        if not projects:
            logger.info("no projects found")
            return

        insights = create_insights(projects=projects)

        logger.info(f"created insights: {len(projects)=}, {len(insights)=}")
