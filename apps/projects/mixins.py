from django.utils.translation import gettext_lazy as _

from adhocracy4.projects.mixins import DisplayProjectOrModuleMixin
from apps.projects.models import ProjectInsight


def create_insight_context(insight: ProjectInsight) -> dict:
    return dict(
        insight=_(str(insight)),
        insight_label=_(
            """This session will provide you with valuable insights
            into the number of individuals invloved in the process
            and help you make informed decisions based on the data"""
        ),
        counts=[
            (_("active participants"), insight.active_participants.count()),
            (_("comments"), insight.comments),
            (_("ratings"), insight.ratings),
            (_("written ideas"), insight.written_ideas),
            (_("poll answers"), insight.poll_answers),
            (_("interactive event questions"), insight.live_questions),
        ],
    )


class DisplayProjectOrModuleMixin(DisplayProjectOrModuleMixin):
    """Overrides Adhocracy4 mixin as to extend
    context for single or multimodules project"""

    def get_context_data(self, **kwargs):
        """Append insights to the template context."""

        context = super().get_context_data(**kwargs)

        insight, created = ProjectInsight.objects.get_or_create(project=self.project)
        print("INSIGHT ", insight)
        print("INSIGHT DISPLAY", insight.display)
        if insight.display:
            context.update(create_insight_context(insight=insight))

        context["result_title"] = _("Final Results")

        return context
