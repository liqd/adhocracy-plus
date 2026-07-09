from apps.projects.models import ProjectInsight
from apps.projects.timeline import build_participation_grid_modules
from apps.projects.timeline import build_participation_timeline_groups
from apps.projects.utils import is_ai_summarisation_enabled


class ProjectDetailDisplayMixin:
    """Shared context for project detail and dashboard preview views."""

    def get_project_detail_context(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["participation_grid_modules"] = build_participation_grid_modules(
            self.project
        )
        context["participation_timeline_groups"] = build_participation_timeline_groups(
            self.project
        )
        context["event"] = None
        context["modules"] = None
        context["ai_summarisation_enabled"] = is_ai_summarisation_enabled(self.project)
        ProjectInsight.update_context(self.project, context)
        return context

    def get_context_data(self, **kwargs):
        return self.get_project_detail_context(**kwargs)
