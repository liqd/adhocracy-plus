# notifications/strategies/project_updates.py
from django.contrib.auth import get_user_model
from adhocracy4.actions.verbs import Verbs
from .base import BaseNotificationStrategy

User = get_user_model()

class ProjectUpdatesStrategy(BaseNotificationStrategy):
    """Handles notifications for updates in followed projects."""
    
    def can_handle(self, action) -> bool:
        return (action.type == "phase" and 
                action.verb in [Verbs.START, Verbs.SCHEDULE])
    
    def get_in_app_recipients(self, action) -> list[User]:
        if not action.project:
            return []
        return User.objects.filter(
            follow__project=action.project,
            follow__enabled=True,
            notification_settings__notify_project_updates=True
        ).distinct()
    
    def should_send_email(self, user) -> bool:
        return user.notification_settings.email_project_updates