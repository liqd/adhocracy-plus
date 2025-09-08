from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from apps.offlineevents.models import OfflineEvent
from apps.moderatorfeedback.models import ModeratorCommentFeedback
from ..strategies import ModeratorFeedbackStrategy
from .helpers import _create_notifications
from ..models import NotificationType

@receiver(post_save, sender=ModeratorCommentFeedback)
def handle_moderator_feedback(sender, instance, **kwargs):
    strategy = ModeratorFeedbackStrategy()
    _create_notifications(instance, strategy, NotificationType.MODERATOR_FEEDBACK)

