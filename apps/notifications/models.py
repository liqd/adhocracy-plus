from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import NotificationManager
from django.contrib.auth import get_user_model
from django.utils import timezone
from adhocracy4.phases.models import Phase
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise
class LazyEncoder(DjangoJSONEncoder):
    """Custom JSON encoder that handles Django's lazy translation objects"""
    def default(self, obj):
        if isinstance(obj, Promise):  # This catches __proxy__ objects
            return str(obj)  # Convert to string
        return super().default(obj)

class PhaseChangeNotification(models.Model):
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name='advance_notifications')
    notification_type = models.CharField(max_length=20, choices=[('start_24h', '24h Before Start'), ('end_24h', '24h Before End')])
    notified_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['phase', 'notification_type']

User = get_user_model()

class NotificationType(models.TextChoices):
    # Project notifications
    PHASE_STARTED = 'phase_started', _('Phase Started')
    PHASE_ENDED = 'phase_ended', _('Phase Ended')
    PROJECT_STARTED = 'project_started', _('Project Started')
    PROJECT_COMPLETED = 'project_completed', _('Project Completed')
    PROJECT_STATUS_CHANGE = 'project_status_change', _('Project Status Change')
    PROJECT_UPDATE = 'project_update', _('Project Update')
    PROJECT_EVENT = 'project_event', _('Project Event')
    EVENT_ADDED = 'event_added', _('Event Added')
    EVENT_SOON = 'event_soon', _('Event Starting Soon')
    EVENT_UPDATE = 'event_update', _('Event Update')
    EVENT_CANCELLED = 'event_cancelled', _('Event Cancelled')
    NEWSLETTER = 'newsletter', _('Newsletter')
    
    # User interactions
    USER_ENGAGEMENT = 'user_engagement', _('User Engagement')
    MESSAGE_RECEIVED = 'message_received', _('Message Received')
    PROJECT_INVITATION = 'project_invitation', _('Project Invitation')
    COMMENT_REPLY = 'comment_reply', _('Comment Reply')
    COMMENT_ON_POST = 'comment_on_post', _('Comment on Post')
    CONTENT_REACTION = 'content_reaction', _('Content Reaction')
    
    # Moderation actions
    MODERATOR_HIGHLIGHT= 'moderator_highlight', _('Moderator Highlight')
    MODERATOR_FEEDBACK = 'moderator_feedback', _('Moderator Feedback')
    MODERATOR_BLOCKED_COMMENT = 'moderator_blocked_comment', _('Moderator Blocked Comment')
    MODERATOR_IDEA_FEEDBACK = 'moderator_idea_feedback', _('Moderator Idea Feedback')
    MODERATOR_ACTION = 'moderator_action', _('Moderator Action')
    CONTENT_APPROVED = 'content_approved', _('Content Approved')
    CONTENT_REJECTED = 'content_rejected', _('Content Rejected')
    USER_WARNING = 'user_warning', _('User Warning')
    CONTENT_FLAGGED = 'content_flagged', _('Content Flagged')
    
    # System
    SYSTEM = 'system', _('System Notification')


class NotificationChannel:
    EMAIL = 'email'
    IN_APP = 'in_app'

class NotificationCategory:
    PROJECT_UPDATES = 'project_updates'
    PROJECT_EVENTS = 'project_events'
    USER_ENGAGEMENT = 'user_engagement'
    MESSAGES = 'messages'
    INVITATIONS = 'invitations'
    MODERATION = 'moderation'
    WARNINGS = 'warnings'

NOTIFICATION_TYPE_MAPPING = {
    # Project notifications
    NotificationType.PHASE_STARTED: NotificationCategory.PROJECT_UPDATES,
    NotificationType.PHASE_ENDED: NotificationCategory.PROJECT_UPDATES,
    NotificationType.PROJECT_STARTED: NotificationCategory.PROJECT_UPDATES,
    NotificationType.PROJECT_COMPLETED: NotificationCategory.PROJECT_UPDATES,
    NotificationType.PROJECT_STATUS_CHANGE: NotificationCategory.PROJECT_UPDATES,
    NotificationType.PROJECT_UPDATE: NotificationCategory.PROJECT_UPDATES,
    
    # Project events
    NotificationType.PROJECT_EVENT: NotificationCategory.PROJECT_EVENTS,
    NotificationType.EVENT_ADDED: NotificationCategory.PROJECT_EVENTS,
    NotificationType.EVENT_SOON: NotificationCategory.PROJECT_EVENTS,
    NotificationType.EVENT_UPDATE: NotificationCategory.PROJECT_EVENTS,
    NotificationType.EVENT_CANCELLED: NotificationCategory.PROJECT_EVENTS,
    
    # User interactions
    NotificationType.USER_ENGAGEMENT: NotificationCategory.USER_ENGAGEMENT,
    NotificationType.COMMENT_REPLY: NotificationCategory.USER_ENGAGEMENT,
    NotificationType.COMMENT_ON_POST: NotificationCategory.USER_ENGAGEMENT,
    NotificationType.CONTENT_REACTION: NotificationCategory.USER_ENGAGEMENT,
    
    # Messages & Invitations
    NotificationType.MESSAGE_RECEIVED: NotificationCategory.MESSAGES,
    NotificationType.PROJECT_INVITATION: NotificationCategory.INVITATIONS,
    
    # Moderation
    NotificationType.MODERATOR_HIGHLIGHT: NotificationCategory.MODERATION,
    NotificationType.MODERATOR_FEEDBACK: NotificationCategory.MODERATION,
    NotificationType.MODERATOR_BLOCKED_COMMENT: NotificationCategory.MODERATION,
    NotificationType.MODERATOR_IDEA_FEEDBACK: NotificationCategory.MODERATION,
    NotificationType.MODERATOR_ACTION: NotificationCategory.MODERATION,
    NotificationType.CONTENT_APPROVED: NotificationCategory.MODERATION,
    NotificationType.CONTENT_REJECTED: NotificationCategory.MODERATION,
    NotificationType.CONTENT_FLAGGED: NotificationCategory.MODERATION,
    NotificationType.USER_WARNING: NotificationCategory.WARNINGS,
    
    # Special cases
    NotificationType.NEWSLETTER: 'newsletter',  # Email only
    NotificationType.SYSTEM: 'system',  # Always on
}

# Field mapping
CATEGORY_TO_FIELDS = {
    NotificationCategory.PROJECT_UPDATES: ('email_project_updates', 'notify_project_updates'),
    NotificationCategory.PROJECT_EVENTS: ('email_project_events', 'notify_project_events'),
    NotificationCategory.USER_ENGAGEMENT: ('email_user_engagement', 'notify_user_engagement'),
    NotificationCategory.MESSAGES: ('email_messages', 'notify_messages'),
    NotificationCategory.INVITATIONS: ('email_invitations', 'notify_invitations'),
    NotificationCategory.MODERATION: ('email_moderation', 'notify_moderation'),
    NotificationCategory.WARNINGS: ('email_warnings', 'notify_warnings'),
    'newsletter': ('email_newsletter', None),  # No in-app for newsletter
    'system': (None, None),  # Always deliver system notifications
}

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

    email_messages = models.BooleanField(default=True, verbose_name=_("Email messages"))
    notify_messages = models.BooleanField(default=True, verbose_name=_("In-app messages"))

    email_invitations = models.BooleanField(default=True, verbose_name=_("Email invitations"))  
    notify_invitations = models.BooleanField(default=True, verbose_name=_("In-app invitations"))

    email_moderation = models.BooleanField(default=True, verbose_name=_("Email moderation actions"))
    notify_moderation = models.BooleanField(default=True, verbose_name=_("In-app moderation actions"))

    email_warnings = models.BooleanField(default=True, verbose_name=_("Email warnings"))
    notify_warnings = models.BooleanField(default=True, verbose_name=_("In-app warnings"))
    
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

    def should_receive_notification(self, notification_type, channel):
        category = NOTIFICATION_TYPE_MAPPING.get(notification_type)
        if not category:
            return False 
        
        if category == 'system':
            return True
        
        email_field, notify_field = CATEGORY_TO_FIELDS.get(category, (None, None))
        
        if channel == NotificationChannel.EMAIL:
            return getattr(self, email_field, False) if email_field else False
        else:  # in_app
            return getattr(self, notify_field, False) if notify_field else False

class Notification(models.Model):
    objects = NotificationManager()

    message_template = models.CharField(max_length=255, default="")
    context = models.JSONField(default=dict, encoder=LazyEncoder)
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
        max_length=30,
        choices=NotificationType.choices,
        verbose_name=_("Notification Type")
    )
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