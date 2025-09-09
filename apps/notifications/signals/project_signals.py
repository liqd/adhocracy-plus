from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from apps.projects.models import ModeratorInvite, ParticipantInvite
from adhocracy4.comments.models import Comment
from ..strategies import ProjectInvitationReceivedStrategy
from ..models import NotificationType
from .helpers import _create_notifications

@receiver(post_save, sender=ParticipantInvite)
def handle_invite_received(sender, instance, created, **kwargs):
    if not created:
        return
    
    strategy = ProjectInvitationReceivedStrategy()
    _create_notifications(instance, strategy)


@receiver(post_save, sender=ModeratorInvite)
def handle_invite_received(sender, instance, created, **kwargs):
    if not created:
        return
    
    strategy = ProjectInvitationReceivedStrategy()
    _create_notifications(instance, strategy)