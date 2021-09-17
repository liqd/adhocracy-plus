from django.urls import reverse

from apps.exports.views import DashboardExportView


class PollDashboardExportView(DashboardExportView):
    template_name = 'a4_candy_exports/export_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_export'] = reverse(
            'a4dashboard:poll-comment-export',
            kwargs={
                'organisation_slug': self.module.project.organisation.slug,
                'module_slug': self.module.slug
            })
        return context
