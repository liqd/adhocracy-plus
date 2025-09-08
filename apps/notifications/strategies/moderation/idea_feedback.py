from ..base import BaseNotificationStrategy
from ...models import NotificationType

class IdeaFeedbackStrategy(BaseNotificationStrategy):

    def get_in_app_recipients(self, idea):
        recipients = set()
        if idea.creator:
            # TODO: Check user preferences
            recipients.add(idea.creator)
        
        return recipients
    
    def get_email_recipients(self, idea):
        return self.get_in_app_recipients(idea)
    
    def create_notification_data(self, idea):
        from django.utils.translation import gettext_lazy as _
        return {
            'notification_type': NotificationType.MODERATOR_IDEA_FEEDBACK,
            'message_template': _("A moderator gave feedback on your idea {idea}"),
            'context': {
                'idea_url': idea.get_absolute_url(),
                'idea': idea.name,
            }
        }