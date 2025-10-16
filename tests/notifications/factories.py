import factory
from django.utils import timezone

from apps.notifications.models import Notification
from apps.notifications.models import NotificationType


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    recipient = factory.SubFactory("tests.factories.UserFactory")
    notification_type = NotificationType.SYSTEM
    message_template = factory.Faker("sentence")
    context = factory.Dict({"example": "value"})
    read = False
    read_at = None
    created = factory.LazyFunction(timezone.now)

    # Optional: Add specific types as class methods
    @classmethod
    def create_project_started(cls, **kwargs):
        return cls.create(
            notification_type=NotificationType.PROJECT_STARTED,
            message_template="The project {project} has begun.",
            **kwargs
        )

    @classmethod
    def create_comment_reply(cls, **kwargs):
        return cls.create(
            notification_type=NotificationType.COMMENT_REPLY,
            message_template="{user} replied to your comment",
            **kwargs
        )

    @classmethod
    def create_event_added(cls, **kwargs):
        return cls.create(
            notification_type=NotificationType.EVENT_ADDED,
            message_template="A new event '{event}' has been added",
            **kwargs
        )
