from ..base import BaseNotificationStrategy
from ...models import NotificationType
class CommentBlockedStrategy(BaseNotificationStrategy):
    """Strategy for notifications when a comment is blocked by a moderator"""
    
    def get_in_app_recipients(self, comment):
        recipients = set()
        if comment.creator and hasattr(comment, 'creator'):
            recipients.add(comment.creator)
        
        return recipients
    
    def get_email_recipients(self, comment):
        return self.get_in_app_recipients(comment)
    
    def create_notification_data(self, comment):
        from django.utils.translation import gettext_lazy as _
        return {
            'notification_type': NotificationType.MODERATOR_BLOCKED_COMMENT,
            'message_template': _("A moderator blocked your comment '{comment}' in project {project}"),
            'context': {
                'project': comment.project.name if comment.project else '',
                'project_url': comment.project.get_absolute_url() if comment.project else '#',
                'comment': comment.comment,
                'comment_url': comment.get_absolute_url(),
            }
        }