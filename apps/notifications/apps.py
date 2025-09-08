from django.apps import AppConfig


class Config(AppConfig):
    name = "apps.notifications"
    label = "notifications"

    def ready(self):
        from .strategies import CommentReplyStrategy, ProjectCommentStrategy, OfflineEventDeletedStrategy, OfflineEventReminderStrategy, OfflineEventUpdateStrategy, PhaseStartedStrategy, PhaseEndedStrategy

        from . import signals