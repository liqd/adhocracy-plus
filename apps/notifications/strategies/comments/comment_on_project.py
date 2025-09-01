from ..base import BaseNotificationStrategy

class ProjectCommentStrategy(BaseNotificationStrategy):
    """Strategy for notifications when someone comments on a project"""
    
    def get_in_app_recipients(self, comment):
        """Get recipients for in-app notifications (project author)"""
        recipients = set()
        
        # Notify the project author/creator
        # TODO: FIX creator finding / sending
        if comment.module and hasattr(comment.module, 'creator'):
            recipients.add(comment.module.creator)
        
        return recipients
    
    def get_email_recipients(self, comment):
        """Get recipients for email notifications (project author)"""
        return self.get_in_app_recipients(comment)
    
    def create_notification_data(self, comment):
        """Create notification data for project comments"""
        from django.utils.translation import gettext_lazy as _
        
        return {
            'notification_type': 'project_comment',
            'title': _("New comment on your project"),
            'message': _("Someone commented on your project '{}'").format(comment.project.name),
            'target_url': comment.get_absolute_url(),
            'context': {
                'project_id': comment.project.id,
                'project_name': comment.project.name,
                'comment_id': comment.id,
                'comment_text': comment.comment[:200] + '...' if len(comment.comment) > 200 else comment.comment
            }
        }