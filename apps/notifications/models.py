from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import NotificationManager
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class NotificationSettings(models.Model):
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_settings",
    )
    
     # Project related - Email newsletter
    email_newsletter = models.BooleanField(
        default=True,
        verbose_name=_("Email newsletter")
    )
    
    # Project related - Project updates
    email_project_updates = models.BooleanField(
        default=True,
        verbose_name=_("Email project updates")
    )
    notify_project_updates = models.BooleanField(
        default=True,
        verbose_name=_("In-app project updates")
    )
    
    # Project related - Project events
    email_project_events = models.BooleanField(
        default=True,
        verbose_name=_("Email project events")
    )
    notify_project_events = models.BooleanField(
        default=True,
        verbose_name=_("In-app project events")
    )
    
    # User interactions
    email_user_engagement = models.BooleanField(
        default=True,
        verbose_name=_("Email user interactions")
    )
    notify_user_engagement = models.BooleanField(
        default=True,
        verbose_name=_("In-app user interactions")
    )
    
    # Tracking settings (in-app notifications)
    track_project_updates = models.BooleanField(default=True)
    track_project_events = models.BooleanField(default=True)
    track_user_engagement = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Notification Settings")
        verbose_name_plural = _("Notification Settings")
    
    def __str__(self):
        return f"Notification settings for {self.user}"
    
    def get_email_fields(self):
        """Return all email preference fields"""
        return [
            'email_project_updates',
            'email_project_events', 
            'email_user_engagement',
            'email_newsletter'
        ]
    
    def get_notification_fields(self):
        """Return all notification toggle fields"""
        return [
            'notify_project_updates',
            'notify_project_events',
            'notify_user_engagement'
        ]
    
    def update_settings(self, **kwargs):
        """Update settings with validation"""
        for field in self.get_email_fields() + self.get_notification_fields():
            if field in kwargs:
                setattr(self, field, kwargs[field])
        self.save()


class NotificationType(models.TextChoices):
    PROJECT_UPDATE = 'project_update', _('Project Update')
    PROJECT_EVENT = 'project_event', _('Project Event')
    USER_ENGAGEMENT = 'user_engagement', _('User Engagement')
    MODERATOR_FEEDBACK = 'moderator_feedback', _('Moderator Feedback')
    NEWSLETTER = 'newsletter', _('Newsletter')
    SYSTEM = 'system', _('System Notification')

class Notification(models.Model):
    objects = NotificationManager()

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    action = models.ForeignKey(
        "a4actions.Action",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        verbose_name=_("Notification Type")
    )
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    message = models.TextField(verbose_name=_("Message"))
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    # Optional links
    target_url = models.URLField(null=True, blank=True, verbose_name=_("Target URL"))
    
    class Meta:
        ordering = ['-created']
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
    
    def __str__(self):
        return f"{self.notification_type} notification for {self.recipient}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save()
    
    @classmethod
    def create_notification(cls, recipient, notification_type, title, message, 
                          action=None, target_url=None, **kwargs):
        """Create a new notification with type validation"""
        return cls.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            action=action,
            target_url=target_url,
            **kwargs
        )