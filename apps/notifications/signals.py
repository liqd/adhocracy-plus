from django.db import transaction
from django.db.models import signals
from django.dispatch import receiver
import logging

from adhocracy4.actions.models import Action
from adhocracy4.follows.models import Follow
from adhocracy4.projects.models import Project

from adhocracy4.dashboard import signals as dashboard_signals

from .services import NotificationService
from .strategies import (
    PublishNotificationStrategy,
    ProjectEventsStrategy,
    ModeratorFeedbackStrategy,
    ProjectCreationStrategy,
    CommentNotificationStrategy
)

# Initialize service with strategies
notification_service = NotificationService([
    PublishNotificationStrategy(),
    ProjectEventsStrategy(),
    ModeratorFeedbackStrategy(),
    ProjectCreationStrategy(),
    CommentNotificationStrategy() 
])

@receiver(signals.post_save, sender=Action)
@transaction.atomic
def handle_action_notifications(instance, created, **kwargs):
    """Unified handler for all action-based notifications"""
    if not created:  # Only handle new actions
        return
    
    action = instance
    notification_service.handle_action(action)

@receiver(dashboard_signals.project_created)
def handle_project_creation(**kwargs):
    project = kwargs.get("project")
    creator = kwargs.get("user")
    notification_service.handle_project_creation(project, creator)

@receiver(signals.m2m_changed, sender=Project.moderators.through)
def autofollow_project_moderators(instance, action, pk_set, reverse, **kwargs):
    if action == "post_add":
        autofollow_project(instance, pk_set, reverse)


def autofollow_project(instance, pk_set, reverse):
    """Auto-follow project when added as moderator"""
    try:
        if not reverse:
            project = instance
            users_pks = pk_set

            for user_pk in users_pks:
                Follow.objects.update_or_create(
                    project=project, 
                    creator_id=user_pk, 
                    defaults={"enabled": True}
                )
        else:
            user = instance
            project_pks = pk_set

            for project_pk in project_pks:
                Follow.objects.update_or_create(
                    project_id=project_pk, 
                    creator=user, 
                    defaults={"enabled": True}
                )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error in autofollow_project: {e}")