from abc import ABC
from abc import abstractmethod

from django.contrib.auth import get_user_model

User = get_user_model()


class BaseNotificationStrategy(ABC):
    """Abstract base class for all notification strategies"""

    def get_organisation(self, obj):
        if hasattr(obj, "organisation"):
            return obj.organisation
        elif hasattr(obj, "project"):
            return obj.project.organisation
        pass

    @abstractmethod
    def get_recipients(self, obj) -> list[User]:
        """Get all potential recipients (before preference filtering)"""
        pass

    @abstractmethod
    def create_notification_data(self, obj) -> dict:
        """Create notification data for a specific recipient"""
        pass
