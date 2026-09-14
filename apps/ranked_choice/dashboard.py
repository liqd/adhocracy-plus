from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from adhocracy4.dashboard import DashboardComponent
from adhocracy4.dashboard import components

from . import exports


class ExportRankedChoiceComponent(DashboardComponent):
    identifier = "ranked_choice_export"
    weight = 50
    label = _("Export ranked-choice results")

    def is_effective(self, module):
        return (
            module.blueprint_type == "RC"
            and not module.project.is_draft
            and not module.is_draft
        )

    def get_progress(self, module):
        return 0, 0

    def get_base_url(self, module):
        return reverse(
            "a4dashboard:ranked-choice-export-module",
            kwargs={
                "organisation_slug": module.project.organisation.slug,
                "module_slug": module.slug,
            },
        )

    def get_urls(self):
        return [
            (
                r"^modules/(?P<module_slug>[-\w_]+)/export/ranked-choice/$",
                exports.RankedBallotExportView.as_view(),
                "ranked-choice-export-module",
            ),
        ]


components.register_module(ExportRankedChoiceComponent())