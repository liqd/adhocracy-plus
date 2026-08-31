from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from adhocracy4.models import base as a4_base
from adhocracy4.modules import models as module_models


class RankedChoice(models.Model):
    """Per-module settings container for a ranked-choice vote.

    One instance exists per module and stores the counting settings.
    """

    module = models.OneToOneField(
        module_models.Module,
        on_delete=models.CASCADE,
        related_name="ranked_choice",
    )
    num_winners = models.PositiveSmallIntegerField(
        default=3,
        verbose_name=_("Number of winners"),
        help_text=_(
            "How many ideas should be selected from the ranked votes. The "
            "top N ideas are considered the winners."
        ),
    )
    hide_results_until_finished = models.BooleanField(
        default=True,
        verbose_name=_("Hide results until participation is over"),
    )

    class Meta:
        verbose_name = _("Ranked choice")
        verbose_name_plural = _("Ranked choices")

    def __str__(self):
        return "Ranked choice in module {}".format(self.module)


class RankedBallot(a4_base.UserGeneratedContentModel):
    """A single voter's ranked ballot for one module.

    One ballot per user per module. Entries are stored ordered by ascending
    ``rank`` (1 = highest preference). Only the ideas the user actually
    ranked are stored; unranked ideas simply do not appear.
    """

    module = models.ForeignKey(
        module_models.Module,
        on_delete=models.CASCADE,
        related_name="ranked_ballots",
    )

    class Meta:
        ordering = ["-created"]
        unique_together = ("module", "creator")

    @property
    def project(self):
        return self.module.project

    def __str__(self):
        return "Ballot by {} in module {}".format(self.creator_id, self.module_id)


class RankedEntry(models.Model):
    """One ranked choice within a ballot, pointing to an idea."""

    ballot = models.ForeignKey(
        RankedBallot,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_pk = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_pk")
    rank = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["rank", "id"]
        unique_together = ("ballot", "content_type", "object_pk")
        indexes = [
            models.Index(fields=["content_type", "object_pk"]),
        ]

    def __str__(self):
        return "Rank {0} for object {1}".format(self.rank, self.object_pk)