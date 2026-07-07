from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from apps import logger
from apps.projects.insights import create_insight
from apps.projects.insights import insight_count_changes
from apps.projects.insights import snapshot_insight_counts
from apps.projects.models import Project
from apps.projects.models import ProjectInsight


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

        corrected_projects = 0
        for project in projects:
            insight, _ = ProjectInsight.objects.get_or_create(project=project)
            before = snapshot_insight_counts(insight)
            create_insight(project=project)
            insight.refresh_from_db()
            changes = insight_count_changes(before, snapshot_insight_counts(insight))

            if not changes:
                continue

            corrected_projects += 1
            formatted = ", ".join(
                f"{field} {old_value} -> {new_value}"
                for field, old_value, new_value in changes
            )
            self.stdout.write(f"{project.slug}: {formatted}")

        logger.info(
            "reset insights: "
            f"{len(projects)} project(s), {corrected_projects} corrected"
        )
