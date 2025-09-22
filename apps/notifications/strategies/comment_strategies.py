from .base import BaseNotificationStrategy
from ..models import NotificationType

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from typing import List

User = get_user_model()


class CommentHighlighted(BaseNotificationStrategy):
    """Strategy for notifications when someone comments on a project"""
    
    def get_in_app_recipients(self, comment) -> List[User]:
        """Get recipients for in-app notifications (project author)"""
        recipients = set()
        if comment.creator and hasattr(comment, 'creator'):
            recipients.add(comment.creator)
        
        return list(recipients)
    
    def get_email_recipients(self, comment) -> List[User]:
        """Get recipients for email notifications (project author)"""
        return self.get_in_app_recipients(comment)
    
    def create_notification_data(self, comment) -> dict:
        """Create notification data for project comments"""
        from django.utils.translation import gettext_lazy as _
        return {
            'notification_type': NotificationType.MODERATOR_HIGHLIGHT,
            'message_template': _("A moderator highlighted your comment '{comment}' in project {project}"),
            'context': {
                'project': comment.project.name if comment.project else '',
                'project_url': comment.project.get_absolute_url() if comment.project else '#',
                'comment': comment.comment,
                'comment_url': comment.get_absolute_url(),
            }
        }


class ProjectComment(BaseNotificationStrategy):
    """Strategy for notifications when someone comments on a project"""
    
    def get_in_app_recipients(self, comment) -> List[User]:
        """Get recipients for in-app notifications (project author)"""
        recipients = set()
        if comment.content_object and hasattr(comment.content_object, 'creator'):
            # TODO: Check user preferences
            recipients.add(comment.content_object.creator)
        
        return list(recipients)
    
    def get_email_recipients(self, comment) -> List[User]:
        """Get recipients for email notifications (project author)"""
        return self.get_in_app_recipients(comment)
    
    def create_notification_data(self, comment) -> dict:
        """Create notification data for project comments"""
        from django.utils.translation import gettext_lazy as _
        return {
            'notification_type': NotificationType.COMMENT_ON_POST,
            'message_template': _("{user} commented on your post {post}"),
            'context': {
                'user': comment.creator.username,
                'user_url': comment.creator.get_absolute_url() if hasattr(comment.creator, 'get_absolute_url') else '',
                'post_url': comment.content_object.get_absolute_url(),
                'post': comment.content_object.name,
            }
        }


class CommentReply(BaseNotificationStrategy):
    """Handles notifications when someone replies to a user's comment"""

    def get_in_app_recipients(self, comment) -> List[User]:
        parent_comment = self._get_parent_comment(comment)
        if parent_comment and parent_comment.creator:
            return [parent_comment.creator] if parent_comment.creator.notification_settings.should_receive_notification(NotificationType.COMMENT_REPLY, 'in_app') else []
        return []
    
    def get_email_recipients(self, comment) -> List[User]:
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