from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from adhocracy4.comments.models import Comment
from ..strategies import CommentReplyStrategy, ProjectCommentStrategy, CommentHighlightedStrategy
from ..models import NotificationType
from .helpers import _create_notifications

@receiver(post_save, sender=Comment)
def handle_comment_notifications(sender, instance, created, **kwargs):
    """Handle all comment-related notifications"""
    if not created:
        return
    
    # Handle comment replies
    if instance.parent_comment.exists():
        strategy = CommentReplyStrategy()
        _create_notifications(instance, strategy, NotificationType.COMMENT_REPLY)
    
    # Handle project comments
    elif instance.project and instance.content_object != instance.project:
        strategy = ProjectCommentStrategy()
        _create_notifications(instance, strategy, NotificationType.COMMENT_ON_POST)


@receiver(pre_save, sender=Comment)
def handle_comment_highlighted(sender, instance, **kwargs):
    """Handle event update/reschedule notifications"""
    if instance.id is None:
        return  # Only handle updates, not creations
    
    previous = Comment.objects.get(id=instance.id)

    was_previously_marked = previous.is_moderator_marked
    is_now_marked = instance.is_moderator_marked
    # Check if important fields changed
    if not was_previously_marked and is_now_marked:
        strategy = CommentHighlightedStrategy()
        _create_notifications(instance, strategy, 'event_update')