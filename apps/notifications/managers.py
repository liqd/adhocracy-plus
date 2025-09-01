from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class NotificationManager(models.Manager):

    def for_user(self, user):
        return self.filter(recipient=user)
    
    def unread_for_user(self, user):
        return self.for_user(user).filter(read=False)
    
    def unread_count_for_user(self, user):
        return self.unread_for_user(user).count()

        
    def create_user_engagement_notification(self, action, recipient):
        """Create notification for user engagement (comments, ratings)"""
        if not recipient.notification_settings.notify_user_engagement:
            return None
            
        return self.create_notification(
            recipient=recipient,
            notification_type=NotificationType.USER_ENGAGEMENT,
            title=_("New reaction to your content"),
            message=_("Someone interacted with your content in {}").format(action.project.name),
            action=action,
            target_url=action.target.get_absolute_url() if hasattr(action.target, 'get_absolute_url') else None
        )
    
    def create_project_update_notification(self, action, recipients):
        """Create notifications for project updates (phase changes)"""
        notifications = []
        for recipient in recipients:
            if recipient.notification_settings.notify_project_updates:
                notifications.append(
                    Notification(
                        recipient=recipient,
                        notification_type=NotificationType.PROJECT_UPDATE,
                        title=_("Project update: {}").format(action.project.name),
                        message=_("There's a new update in a project you're following"),
                        action=action,
                        target_url=action.project.get_absolute_url()
                    )
                )
        return self.bulk_create(notifications)
    
    def create_project_event_notification(self, action, recipients):
        """Create notifications for project events"""
        notifications = []
        for recipient in recipients:
            if recipient.notification_settings.notify_project_events:
                notifications.append(
                    Notification(
                        recipient=recipient,
                        notification_type=NotificationType.PROJECT_EVENT,
                        title=_("Upcoming event: {}").format(action.target.title),
                        message=_("An event is starting soon in {}").format(action.project.name),
                        action=action,
                        target_url=action.target.get_absolute_url() if hasattr(action.target, 'get_absolute_url') else None
                    )
                )
        return self.bulk_create(notifications)

    def get_unread_for_user(self, user):
        """Get all unread notifications for a user"""
        return self.filter(recipient=user, read=False)
    
    def mark_as_read(self, notification_id, user):
        """Mark a specific notification as read"""
        notification = self.filter(id=notification_id, recipient=user).first()
        if notification and not notification.read:
            notification.read = True
            notification.read_at = timezone.now()
            notification.save()
        return notification