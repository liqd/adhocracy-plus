from django.db.models.signals import post_save
from django.dispatch import receiver
from adhocracy4.comments.models import Comment
from ..strategies import CommentReplyStrategy, ProjectCommentStrategy
from .helpers import _create_notifications

@receiver(post_save, sender=Comment)
def handle_comment_notifications(sender, instance, created, **kwargs):
    """Handle all comment-related notifications"""
    if not created:
        return
    
    # Handle comment replies (existing functionality)
    if instance.parent_comment.exists():
        strategy = CommentReplyStrategy()
        _create_notifications(instance, strategy, 'comment_reply')
    
    # Handle project comments (new functionality)
    elif instance.project and instance.content_object != instance.project:
        strategy = ProjectCommentStrategy()
        _create_notifications(instance, strategy, 'project_comment')