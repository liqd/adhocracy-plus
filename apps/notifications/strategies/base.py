from abc import ABC
from abc import abstractmethod

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

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

    def _get_moderator_status_display(self, obj):
        """Shared method for all moderator status displays."""
        status = getattr(obj, "moderator_status", None)
        if status:
            status = status.lower()
            status_map = {
                "accepted": _("Your submission was accepted"),
                "approved": _("Your submission was approved"),
                "rejected": _("Your submission was rejected"),
                "reviewed": _("Your submission was reviewed"),
                "consideration": _("Your submission is under consideration"),
            }
            return status_map.get(status, status)
        return ""
