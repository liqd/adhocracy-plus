from django.db import models
from django.utils.translation import ugettext_lazy as _

from adhocracy4.comments.models import Comment
from adhocracy4.models import base

CLASSIFICATION_CHOICES = (
    ('OFFENSIVE', _('Offensive')),
    ('OTHER', _('Other')),
)


class Classification(models.Model):

    class Meta:
        abstract = True

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE
    )

    classification = models.CharField(max_length=50,
                                      choices=CLASSIFICATION_CHOICES)
    comment_text = models.TextField(max_length=4000)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.comment_text = self.comment.comment
        super().save(*args, **kwargs)


"""
We use the a4 reports for user classifications for now
until we decided on a final reporting/classification procedure.
Since we would have to disconnect reports and instead connect
UserClassification to the comments, this seemed too complicated
without a clear goal.
The reports can then be shown in moderation dashboard without
a classification.
"""

"""
class UserClassification(Classification, base.UserGeneratedContentModel):

    user_message = models.TextField(max_length=1024)
"""


class AIClassification(Classification, base.TimeStampedModel):

    pass
