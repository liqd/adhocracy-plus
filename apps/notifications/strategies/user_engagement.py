from django.contrib.auth import get_user_model
from adhocracy4.actions.verbs import Verbs
from .base import BaseNotificationStrategy

User = get_user_model()

class UserEngagementStrategy(BaseNotificationStrategy):
    """Handles notifications when users react to user's content."""
    
    def can_handle(self, action) -> bool:
        verb = Verbs(action.verb)
        has_creator = hasattr(action.target, 'creator')
        is_engagement = action.type in ['comment', 'rating', 'reaction']
        not_self_engagement = has_creator and action.actor != action.target.creator
        
        return (has_creator and 
                verb in [Verbs.CREATE, Verbs.ADD] and 
                is_engagement and 
                not_self_engagement)
    
    def get_in_app_recipients(self, action) -> list[User]:
        creator = action.target.creator
        if (creator and 
            creator.notification_settings.notify_user_engagement):
            return [creator]
        return []
    
    def should_send_email(self, user) -> bool:
        return user.notification_settings.email_user_engagement