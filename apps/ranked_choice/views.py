from django.utils import timezone
from django.views import generic

from adhocracy4.projects.mixins import DisplayProjectOrModuleMixin
from adhocracy4.projects.mixins import ProjectMixin
from adhocracy4.rules import mixins as rules_mixins

from apps.ideas.models import Idea

from . import apps
from .models import RankedBallot
from .models import RankedChoice
from .tally import tally


class RankedChoiceDetailView(
    ProjectMixin,
    rules_mixins.PermissionRequiredMixin,
    generic.TemplateView,
    DisplayProjectOrModuleMixin,
):
    template_name = "a4_candy_ranked_choice/ranked_choice_detail.html"
    permission_required = "a4projects.view_project"

    def get_permission_object(self):
        return self.project

    def get(self, request, *args, **kwargs):
        self.ranked_choice, _ = RankedChoice.objects.get_or_create(module=self.module)
        self.ideas = list(
            Idea.objects.filter(module=self.module).order_by("created", "pk")
        )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["module"] = self.module
        context["project"] = self.project
        context["ranked_choice"] = self.ranked_choice
        context["ideas"] = self.ideas
        context["my_ballot"] = self._my_ballot()
        context["user_can_rank"] = self.request.user.has_perm(
            "a4_candy_ranked_choice.rank_idea", self.module
        )
        results_visible = self._results_visible()
        context["results_visible"] = results_visible
        context["winners"] = self._winners() if results_visible else []
        return context

    def _my_ballot(self):
        user = self.request.user
        if not user.is_authenticated:
            return []
        ballot = RankedBallot.objects.filter(module=self.module, creator=user).first()
        if not ballot:
            return []
        return list(
            ballot.entries.order_by("rank", "id").values_list("object_pk", flat=True)
        )

    def _results_visible(self):
        ranked_choice = self.ranked_choice
        if not ranked_choice.hide_results_until_finished:
            return True
        rank_type = "{}:rank".format(apps.Config.label)
        rank_phase = self.module.phases.filter(type=rank_type).first()
        if not rank_phase:
            return False
        return rank_phase.end_date < timezone.now()

    def _winners(self):
        ballots = []
        for ballot in self.module.ranked_ballots.all():
            ballots.append(
                list(
                    ballot.entries.order_by("rank", "id").values_list(
                        "object_pk", flat=True
                    )
                )
            )
        candidates = [idea.pk for idea in self.ideas]
        winners = tally(ballots, candidates, self.ranked_choice.num_winners)
        by_pk = {idea.pk: idea for idea in self.ideas}
        return [
            {"place": offset + 1, "idea": by_pk[pk]}
            for offset, pk in enumerate(winners)
        ]