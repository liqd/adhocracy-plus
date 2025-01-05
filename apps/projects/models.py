import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from adhocracy4.models import base
from adhocracy4.projects.models import Project

from . import emails


class Invite(base.TimeStampedModel):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    site = models.CharField(max_length=200)

    class Meta:
        abstract = True

    def accept(self, user):
        self.delete()

    def reject(self):
        self.delete()


class ParticipantInviteManager(models.Manager):
    def invite(self, creator, project, email, site):
        invite = super().create(
            project=project, creator=creator, email=email, site=site
        )
        emails.InviteParticipantEmail.send(invite)
        return invite


class ParticipantInvite(Invite):
    objects = ParticipantInviteManager()

    def __str__(self):
        return "Participation invite to {s.project} for {s.email}".format(s=self)

    def get_absolute_url(self):
        url_kwargs = {
            "organisation_slug": self.project.organisation.slug,
            "invite_token": self.token,
        }
        return reverse("project-participant-invite-detail", kwargs=url_kwargs)

    def accept(self, user):
        self.project.participants.add(user)
        super().accept(user)

    class Meta:
        unique_together = ("email", "project")


class ModeratorInviteManager(models.Manager):
    def invite(self, creator, project, email, site):
        invite = super().create(
            project=project, creator=creator, email=email, site=site
        )
        emails.InviteModeratorEmail.send(invite)
        return invite


class ModeratorInvite(Invite):
    objects = ModeratorInviteManager()

    def __str__(self):
        return "Moderation invite to {s.project} for {s.email}".format(s=self)

    def get_absolute_url(self):
        url_kwargs = {
            "organisation_slug": self.project.organisation.slug,
            "invite_token": self.token,
        }
        return reverse("project-moderator-invite-detail", kwargs=url_kwargs)

    def accept(self, user):
        self.project.moderators.add(user)
        super().accept(user)

    class Meta:
        unique_together = ("email", "project")


class ProjectInsight(base.TimeStampedModel):
    project = models.OneToOneField(
        Project, related_name="insight", on_delete=models.CASCADE
    )
    active_participants = models.ManyToManyField(settings.AUTH_USER_MODEL)
    unregistered_participants = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    ratings = models.PositiveIntegerField(default=0)
    written_ideas = models.PositiveIntegerField(default=0)
    poll_answers = models.PositiveIntegerField(default=0)
    live_questions = models.PositiveIntegerField(default=0)
    display = models.BooleanField(default=False)

    @staticmethod
    def update_context(project, context, dashboard=False):
        insight, created = ProjectInsight.objects.get_or_create(project=project)
        if dashboard or insight.display:
            context.update(create_insight_context(insight=insight))
        return context

    def __str__(self):
        return "Insights for project %s" % self.project.name


def create_insight_context(insight: ProjectInsight) -> dict:
    """
    ("BS", _("brainstorming")),
    ("MBS", _("spatial brainstorming")),
    ("IC", _("idea challenge")),
    ("MIC", _("spatial idea challenge")),
    ("TR", _("text review")),
    ("PO", _("poll")),
    ("PB", _("participatory budgeting")),
    ("IE", _("interactive event")),
    ("TP", _("prioritization")),
    ("DB", _("debate")),
    """

    active_modules = [
        module for module in insight.project.modules if not module.is_draft
    ]
    blueprint_types = {module.blueprint_type for module in active_modules}
    show_polls = "PO" in blueprint_types
    show_live_questions = "IE" in blueprint_types
    show_ideas = bool(blueprint_types.intersection({"BS", "IC", "MBS", "MIC", "PB"}))

    counts = [
        (
            _("active participants"),
            insight.active_participants.count() + insight.unregistered_participants,
        ),
        (_("comments"), insight.comments),
        (_("ratings"), insight.ratings),
    ]

    if show_ideas:
        counts.append((_("written ideas"), insight.written_ideas))

    if show_polls:
        counts.append((_("poll answers"), insight.poll_answers))

    if show_live_questions:
        counts.append((_("interactive event questions"), insight.live_questions))

    return dict(
        insight_label=_(
            """This section provides an overview of the participation
            activities in this project."""
        ),
        counts=counts,
    )
