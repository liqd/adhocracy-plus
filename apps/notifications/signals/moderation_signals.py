from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from apps.ideas.models import Idea
from apps.offlineevents.models import OfflineEvent
from apps.moderatorfeedback.models import ModeratorCommentFeedback
from ..strategies import ModeratorFeedbackStrategy, IdeaFeedbackStrategy
from .helpers import _create_notifications
from ..models import NotificationType

@receiver(post_save, sender=ModeratorCommentFeedback)
def handle_comment_moderator_feedback(sender, instance, **kwargs):
    strategy = ModeratorFeedbackStrategy()
    _create_notifications(instance, strategy, NotificationType.MODERATOR_IDEA_FEEDBACK)

@receiver(pre_save, sender=Idea)
def handle_idea_moderator_feedback(sender, instance, **kwargs):
    previous = Idea.objects.get(id=instance.id)

    old_mod_status = previous.moderator_status 
    old_feedback_text = previous.moderator_feedback_text

    new_mod_status = instance.moderator_status 
    new_feedback_text = instance.moderator_feedback_text

    if old_mod_status != new_mod_status or old_feedback_text != new_feedback_text:
        strategy = IdeaFeedbackStrategy()
        _create_notifications(instance, strategy, NotificationType.MODERATOR_IDEA_FEEDBACK)