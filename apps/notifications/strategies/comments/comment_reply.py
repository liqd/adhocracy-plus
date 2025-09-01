from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from ..base import BaseNotificationStrategy
from ...models import NotificationType

User = get_user_model()

class CommentReplyStrategy(BaseNotificationStrategy):
    """Handles notifications when someone replies to a user's comment"""

    def get_in_app_recipients(self, comment) -> list[User]:
        parent_comment = self._get_parent_comment(comment)
        if parent_comment and parent_comment.creator:
            return [parent_comment.creator] if parent_comment.creator.notification_settings.should_receive_notification(NotificationType.COMMENT_REPLY, 'in_app') else []
        return []
    
    def get_email_recipients(self, comment) -> list[User]:
        parent_comment = self._get_parent_comment(comment)
        if parent_comment and parent_comment.creator:
            return [parent_comment.creator] if parent_comment.creator.notification_settings.should_receive_notification(NotificationType.COMMENT_REPLY, 'email') else []
        return []
    
    def _get_parent_comment(self, comment):
        """Get the parent comment if this is a reply"""
        parent_comments = comment.parent_comment.all()
        return parent_comments.first() if parent_comments.exists() else None
    
    
    def create_notification_data(self, comment) -> dict:
        comment_url = comment.get_absolute_url() if hasattr(comment, 'get_absolute_url') else ''
        
        return {
            'notification_type': NotificationType.COMMENT_REPLY,
            'message_template': _("{user} replied to your {comment}"),
            'context': {
                'user': comment.creator.username,
                'user_url': comment.creator.get_absolute_url() if hasattr(comment.creator, 'get_absolute_url') else '',
                'comment': _("comment"),
                'comment_url': comment_url
            },
        }