# notifications/strategies/newsletter.py
from django.contrib.auth import get_user_model
from .base import BaseNotificationStrategy

User = get_user_model()

class NewsletterStrategy(BaseNotificationStrategy):
    """Handles email newsletter notifications."""
    
    def can_handle(self, action) -> bool:
        return action.type == "newsletter"
    
    def get_in_app_recipients(self, action) -> list[User]:
        return []  # Newsletter is email-only
    
    def get_email_recipients(self, action) -> list[User]:
        return User.objects.filter(notification_settings__email_newsletter=True)