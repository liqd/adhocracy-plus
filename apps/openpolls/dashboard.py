from django.urls import reverse

from adhocracy4.dashboard import components
from adhocracy4.open_poll import dashboard as a4_poll_dashboard
from adhocracy4.open_poll import exports as a4_poll_exports

from . import views


class PollComponent(a4_poll_dashboard.OpenPollComponent):
    def get_base_url(self, module):
        return reverse(
            "a4dashboard:open-poll-dashboard",
            kwargs={
                "organisation_slug": module.project.organisation.slug,
                "module_slug": module.slug,
            },
        )


class ExportPollComponent(a4_poll_dashboard.ExportOpenPollComponent):
    def get_base_url(self, module):
        return reverse(
            "a4dashboard:open-poll-export-module",
            kwargs={
                "organisation_slug": module.project.organisation.slug,
                "module_slug": module.slug,
            },
        )

    def get_urls(self):
        return [
            (
                r"^modules/(?P<module_slug>[-\w_]+)/poll/export/$",
                views.PollDashboardExportView.as_view(),
                "open-poll-export-module",
            ),
            (
                r"^modules/(?P<module_slug>[-\w_]+)/poll/export/comments/$",
                a4_poll_exports.OpenPollCommentExportView.as_view(),
                "opel-poll-comment-export",
            ),
            (
                r"^modules/(?P<module_slug>[-\w_]+)/poll/export/poll/$",
                a4_poll_exports.OpenPollExportView.as_view(),
                "open-poll-export",
            ),
        ]


components.replace_module(PollComponent())
components.replace_module(ExportPollComponent())
