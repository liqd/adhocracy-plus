from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from apps.offlineevents.models import OfflineEvent
from ..strategies import OfflineEventCreatedStrategy,OfflineEventDeletedStrategy,  OfflineEventUpdateStrategy
from .helpers import _create_notifications

@receiver(post_delete, sender=OfflineEvent)
def handle_offline_event_deleted_notifications(sender, instance, **kwargs):
    strategy = OfflineEventDeletedStrategy()
    _create_notifications(instance, strategy, 'event_cancelled')


@receiver(pre_save, sender=OfflineEvent)
def handle_event_update_notifications(sender, instance, **kwargs):
    """Handle event update/reschedule notifications"""
    if instance.id is None:
        return  # Only handle updates, not creations
    
    strategy = OfflineEventUpdateStrategy()
    previous = OfflineEvent.objects.get(id=instance.id)
    # Check if important fields changed
    if previous and previous.date != instance.date:
        print("Processing event update notification...")
        _create_notifications(instance, strategy, 'event_update')

@receiver(post_save, sender=OfflineEvent)
def handle_offline_event_notifications(sender, instance, created, **kwargs):
    """Handle offline event notifications"""
    if created and instance.project:
        print("Processing offline event notification...")
        strategy = OfflineEventCreatedStrategy()
        _create_notifications(instance, strategy, 'offline_event')
