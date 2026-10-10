import csv

from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from adhocracy4.projects.mixins import ProjectMixin

from .models import RankedBallot


class RankedBallotExportView(ProjectMixin, PermissionRequiredMixin, generic.View):
    permission_required = "a4_candy_ranked_choice.moderate_ranked_choice"

    def get_permission_object(self):
        return self.module

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="ranked_choice.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                _("Ballot ID"),
                _("Creator"),
                _("Created"),
                _("Rank"),
                _("Idea reference"),
                _("Idea name"),
                _("Idea link"),
            ]
        )
        ballots = (
            RankedBallot.objects.filter(module=self.module)
            .prefetch_related("entries")
            .order_by("id")
        )
        for ballot in ballots:
            creator = ballot.creator.username if ballot.creator else ""
            for entry in ballot.entries.order_by("rank", "id"):
                idea = entry.content_object
                writer.writerow(
                    [
                        ballot.id,
                        creator,
                        ballot.created,
                        entry.rank,
                        idea.reference_number if idea else entry.object_pk,
                        idea.name if idea else "",
                        idea.get_absolute_url() if idea else "",
                    ]
                )
        return response