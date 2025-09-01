from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import User
from ..models import NotificationSettings

@receiver(post_save, sender=User)
def create_user_notification_settings(sender, instance, created, **kwargs):
    """Automatically create notification settings when a new user is created"""
    if created:
        NotificationSettings.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_notification_settings(sender, instance, **kwargs):
    """Save notification settings when user is saved"""
    instance.notification_settings.save()