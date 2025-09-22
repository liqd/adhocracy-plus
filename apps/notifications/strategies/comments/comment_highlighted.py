from ..base import BaseNotificationStrategy
from ...models import NotificationType
class CommentHighlightedStrategy(BaseNotificationStrategy):
    """Strategy for notifications when someone comments on a project"""
    
    def get_in_app_recipients(self, comment):
        """Get recipients for in-app notifications (project author)"""
        recipients = set()
        if comment.creator and hasattr(comment, 'creator'):
            recipients.add(comment.creator)
        
        return recipients
    
    def get_email_recipients(self, comment):
        """Get recipients for email notifications (project author)"""
        return self.get_in_app_recipients(comment)
    
    def create_notification_data(self, comment):
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