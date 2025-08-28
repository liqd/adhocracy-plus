from django.db.models.signals import post_save
from django.dispatch import receiver

from adhocracy4.notifications.models import NotificationSettings

from .models import User


@receiver(post_save, sender=User)
def create_notification_settings(sender, instance, created, *args, **kwargs):
    """Create notification settings for user"""
    if created and not hasattr(instance, "notification_settings"):
        NotificationSettings.objects.create(user=instance)
