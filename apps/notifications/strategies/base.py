from abc import ABC, abstractmethod
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseNotificationStrategy(ABC):
    """Abstract base class for all notification strategies"""
    
    @abstractmethod
    def get_in_app_recipients(self, obj) -> list[User]:
        """Get users who should receive in-app notifications"""
        pass
        
    @abstractmethod
    def get_email_recipients(self, obj) -> list[User]:
        """Get users who should receive email notifications"""
        pass
        
    @abstractmethod
    def create_notification_data(self, obj) -> dict:
        """Create notification data for a specific recipient"""
        pass