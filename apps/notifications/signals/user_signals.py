from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from apps.users.models import User
from ..models import NotificationSettings

@receiver(pre_save, sender=User)
def create_user_notification_settings(sender, instance, **kwargs):
    NotificationSettings.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_notification_settings(sender, instance, **kwargs):
    """Save notification settings when user is saved"""
    if instance.notification_settings:
        instance.notification_settings.save()
        