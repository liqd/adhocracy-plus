from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import gettext_lazy as _

from adhocracy4 import transforms
from adhocracy4.comments.models import Comment
from adhocracy4.models.base import UserGeneratedContentModel

from . import fields

DEFAULT_CHOICES = (
    ("CONSIDERATION", _("Under consideration")),
    ("REJECTED", _("Rejected")),
    ("ACCEPTED", _("Accepted")),
)


class ModeratorFeedback(UserGeneratedContentModel):
    feedback_text = RichTextField(
        blank=True,
        verbose_name=_("Official feedback"),
        help_text=_(
            "The official feedback will appear below the idea, "
            "indicating your organisation. The idea provider receives "
            "a notification."
        ),
    )

    def save(self, *args, **kwargs):
        self.feedback_text = transforms.clean_html_field(self.feedback_text)
        super().save(*args, **kwargs)


class Moderateable(models.Model):
    moderator_status_choices = DEFAULT_CHOICES

    moderator_status = fields.ModeratorFeedbackField(
        verbose_name=_("Processing status"),
        help_text=_(
            "The editing status appears below the title of the "
            "idea in red, yellow or green. The idea provider receives a "
            "notification."
        ),
    )

    moderator_feedback_text = models.OneToOneField(
        ModeratorFeedback,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class ModeratorCommentFeedback(UserGeneratedContentModel):
    feedback_text = RichTextField(
        blank=True,
        verbose_name=_("Moderator feedback"),
    )
    comment = models.OneToOneField(
        Comment, on_delete=models.CASCADE, related_name="moderator_feedback"
    )

    @property
    def project(self):
        return self.comment.project

    def __str__(self):
        return ("{} - {}").format(self.comment.id, self.feedback_text)
