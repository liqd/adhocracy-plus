from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from ..base import BaseNotificationStrategy
from ...models import NotificationType

User = get_user_model()

class ModeratorFeedbackStrategy(BaseNotificationStrategy):
    """Handles notifications when someone replies to a user's comment"""

    def get_in_app_recipients(self, feedback) -> list[User]:
        user_comment = feedback.comment
        if user_comment and user_comment.creator:
            return [user_comment.creator]
        return []
    
    def get_email_recipients(self, feedback) -> list[User]:
        user_comment = feedback.comment
        if user_comment and user_comment.creator:
            return [user_comment.creator]
        return []
    
    
    def create_notification_data(self, feedback) -> dict:
        user_comment = feedback.comment
        return {
            'notification_type': NotificationType.MODERATOR_FEEDBACK,
            'message_template': _("A moderator gave feedback on your {comment}"),
            'context': {
                'comment': _("comment"),
                'comment_url': user_comment.get_absolute_url()
            },
        }