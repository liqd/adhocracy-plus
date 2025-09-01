from abc import ABC, abstractmethod
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseNotificationStrategy(ABC):
    """Abstract base class for all notification strategies."""
    
    @abstractmethod
    def can_handle(self, action) -> bool:
        pass
    
    @abstractmethod
    def get_in_app_recipients(self, action) -> list[User]:
        pass
    
    def get_email_recipients(self, action) -> list[User]:
        in_app_recipients = self.get_in_app_recipients(action)
        return [user for user in in_app_recipients if self.should_send_email(user)]
    
    def should_send_email(self, user) -> bool:
        return True
    
    def create_notification_data(self, action, recipient):
        return {
            'title': 'Notification',
            'message': 'You have a new notification'
        }