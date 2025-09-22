from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from apps.ideas.models import Idea
from adhocracy4.comments.models import Comment
from apps.budgeting.models import Proposal
from apps.offlineevents.models import OfflineEvent
from apps.moderatorfeedback.models import ModeratorCommentFeedback
from ..strategies import ModeratorFeedback, IdeaFeedback, ProposalFeedback, CommentBlocked
from .helpers import _create_notifications
from ..models import NotificationType

@receiver(post_save, sender=ModeratorCommentFeedback)
def handle_comment_moderator_feedback(sender, instance, **kwargs):
    strategy = ModeratorFeedback()
    _create_notifications(instance, strategy)

@receiver(pre_save, sender=Proposal)
def handle_proposal_moderator_feedback(sender, instance, **kwargs):
    previous = Idea.objects.get(id=instance.id)

    old_mod_status = previous.moderator_status 
    old_feedback_text = previous.moderator_feedback_text

    new_mod_status = instance.moderator_status 
    new_feedback_text = instance.moderator_feedback_text

    if old_mod_status != new_mod_status or old_feedback_text != new_feedback_text:
        strategy = ProposalFeedback()
        _create_notifications(instance, strategy)

@receiver(pre_save, sender=Idea)
def handle_idea_moderator_feedback(sender, instance, **kwargs):
    previous = Idea.objects.get(id=instance.id)

    old_mod_status = previous.moderator_status 
    old_feedback_text = previous.moderator_feedback_text

    new_mod_status = instance.moderator_status 
    new_feedback_text = instance.moderator_feedback_text

    if old_mod_status != new_mod_status or old_feedback_text != new_feedback_text:
        strategy = IdeaFeedback()
        _create_notifications(instance, strategy)

@receiver(pre_save, sender=Comment)
def handle_comment_moderator_feedback(sender, instance, **kwargs):
    """Handle comment being blocked by a moderator"""
    if instance.id is None:
        return  # Only handle updates, not creations
    
    previous = Comment.objects.get(id=instance.id)

    was_previously_blocked = previous.is_blocked
    is_now_blocked = instance.is_blocked

    if not was_previously_blocked and is_now_blocked:
        strategy = CommentBlocked()
        _create_notifications(instance, strategy)
        return

