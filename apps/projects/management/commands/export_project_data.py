import json

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.projects.export_utils import generate_full_export
from apps.projects.models import Project


class Command(BaseCommand):
    help = "Export project data by project name"

    def add_arguments(self, parser):
        parser.add_argument(
            "project_name",
            nargs="?",
            type=str,
            help="Project name to export (partial match allowed)",
        )

    def handle(self, *args, **options):  # noqa: C901
        project_name = options.get("project_name")

        if not project_name:
            project_name = input("Enter project name (or part of it): ")

        # Find projects matching the name
        projects = Project.objects.filter(Q(name__icontains=project_name)).order_by(
            "name"
        )

        if not projects.exists():
            self.stderr.write(
                self.style.ERROR(f'No projects found matching "{project_name}"')
            )
            return

        # If multiple projects found, let user choose
        if projects.count() > 1:
            self.stdout.write(self.style.WARNING(f"Found {projects.count()} projects:"))
            for i, project in enumerate(projects, 1):
                self.stdout.write(f"{i}. {project.name} (ID: {project.id})")

            choice = input("\nSelect project number (or 'all' for all): ").strip()

            if choice.lower() == "all":
                selected_projects = projects
            else:
                try:
                    idx = int(choice) - 1
                    selected_projects = [projects[idx]]
                except (ValueError, IndexError):
                    self.stderr.write(self.style.ERROR("Invalid selection"))
                    return
        else:
            selected_projects = [projects.first()]

        # Export each selected project
        for project in selected_projects:
            self.stdout.write(self.style.SUCCESS(f"\nExporting: {project.name}"))

            try:
                export_data = generate_full_export(project)
                json_output = json.dumps(export_data, indent=2, ensure_ascii=False)

                # Print to console
                self.stdout.write(json_output)

                # Optionally save to file
                filename = f"{project.slug}_export.json"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(json_output)
                self.stdout.write(self.style.SUCCESS(f"Saved to: {filename}"))

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Error exporting {project.name}: {e}")
                )
