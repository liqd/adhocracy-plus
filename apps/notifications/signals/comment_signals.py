from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from adhocracy4.comments.models import Comment
from ..strategies import CommentReply, ProjectComment, CommentHighlighted
from ..models import NotificationType
from .helpers import _create_notifications

@receiver(post_save, sender=Comment)
def handle_comment_notifications(sender, instance, created, **kwargs):
    """Handle all comment-related notifications"""
    if not created:
        return
    
    # Handle comment replies
    if instance.parent_comment.exists():
        strategy = CommentReply()
        _create_notifications(instance, strategy)
    
    # Handle project comments
    elif instance.project and instance.content_object != instance.project:
        strategy = ProjectComment()
        _create_notifications(instance, strategy)


@receiver(pre_save, sender=Comment)
def handle_comment_highlighted(sender, instance, **kwargs):
    """Handle comment being highlighted y auth"""
    if instance.id is None:
        return  # Only handle updates, not creations
    
    previous = Comment.objects.get(id=instance.id)

    was_previously_marked = previous.is_moderator_marked
    is_now_marked = instance.is_moderator_marked
    # Check if important fields changed
    if not was_previously_marked and is_now_marked:
        strategy = CommentHighlighted()
        _create_notifications(instance, strategy)
        return