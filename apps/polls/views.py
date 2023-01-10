from django.urls import reverse

from adhocracy4.exports.views import DashboardExportView


class PollDashboardExportView(DashboardExportView):

    template_name = "a4exports/export_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_export"] = reverse(
            "a4dashboard:poll-comment-export",
            kwargs={
                "organisation_slug": self.module.project.organisation.slug,
                "module_slug": self.module.slug,
            },
        )
        context["poll_export"] = reverse(
            "a4dashboard:poll-export",
            kwargs={
                "organisation_slug": self.module.project.organisation.slug,
                "module_slug": self.module.slug,
            },
        )
        return context
