from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver

from adhocracy4.comments.models import Comment
from apps.budgeting.models import Proposal
from apps.ideas.models import Idea
from apps.moderatorfeedback.models import ModeratorCommentFeedback
from apps.offlineevents.models import OfflineEvent
from apps.projects.models import ModeratorInvite
from apps.projects.models import ParticipantInvite
from apps.projects.models import Project

from .helpers import _create_notifications
from .strategies import CommentBlocked
from .strategies import CommentHighlighted
from .strategies import CommentReply
from .strategies import IdeaFeedback
from .strategies import ModeratorFeedback
from .strategies import OfflineEventCreated
from .strategies import OfflineEventDeleted
from .strategies import OfflineEventUpdate
from .strategies import ProjectComment
from .strategies import ProjectCreated
from .strategies import ProjectDeleted
from .strategies import ProjectInvitationReceived
from .strategies import ProjectModerationInvitationReceived
from .strategies import ProposalFeedback

# Comment Signals


@receiver(post_save, sender=Comment)
def handle_comment_notifications(sender, instance, created, **kwargs):
    """Handle all comment-related notifications"""
    if not created:
        return

    # Handle comment replies
    if instance.parent_comment.exists():
        strategy = CommentReply()
        _create_notifications(instance, strategy)

    # Handle project comments
    elif instance.project and instance.content_object != instance.project:
        strategy = ProjectComment()
        _create_notifications(instance, strategy)


@receiver(pre_save, sender=Comment)
def handle_comment_highlighted(sender, instance, **kwargs):
    """Handle comment being highlighted y auth"""
    if instance.id is None:
        return  # Only handle updates, not creations

    previous = Comment.objects.get(id=instance.id)

    was_previously_marked = previous.is_moderator_marked
    is_now_marked = instance.is_moderator_marked
    # Check if important fields changed
    if not was_previously_marked and is_now_marked:
        strategy = CommentHighlighted()
        _create_notifications(instance, strategy)
        return


# Moderation Signals


@receiver(post_save, sender=ModeratorCommentFeedback)
def handle_comment_moderator_feedback(sender, instance, **kwargs):
    strategy = ModeratorFeedback()
    _create_notifications(instance, strategy)


@receiver(pre_save, sender=Proposal)
def handle_proposal_moderator_feedback(sender, instance, **kwargs):
    if instance.id is None:
        return

    try:
        previous = Proposal.objects.get(id=instance.id)
    except Proposal.DoesNotExist:
        return

    old_mod_status = previous.moderator_status
    old_feedback_text = previous.moderator_feedback_text

    new_mod_status = instance.moderator_status
    new_feedback_text = instance.moderator_feedback_text

    if old_mod_status != new_mod_status or old_feedback_text != new_feedback_text:
        strategy = ProposalFeedback()
        _create_notifications(instance, strategy)


@receiver(pre_save, sender=Idea)
def handle_idea_moderator_feedback(sender, instance, **kwargs):
    """Handle idea moderator feedback notifications"""
    if instance.id is None:
        return

    try:
        previous = Idea.objects.get(id=instance.id)
    except Idea.DoesNotExist:
        return

    old_mod_status = previous.moderator_status
    old_feedback_text = previous.moderator_feedback_text

    new_mod_status = instance.moderator_status
    new_feedback_text = instance.moderator_feedback_text

    if old_mod_status != new_mod_status or old_feedback_text != new_feedback_text:
        strategy = IdeaFeedback()
        _create_notifications(instance, strategy)


@receiver(pre_save, sender=Comment)
def handle_comment_blocked_by_moderator(sender, instance, **kwargs):
    if instance.id is None:
        return

    try:
        previous = Comment.objects.get(id=instance.id)
    except Comment.DoesNotExist:
        return

    was_previously_blocked = previous.is_blocked
    is_now_blocked = instance.is_blocked

    if not was_previously_blocked and is_now_blocked:
        strategy = CommentBlocked()
        _create_notifications(instance, strategy)
        return


# Event Signals


@receiver(post_delete, sender=OfflineEvent)
def handle_offline_event_deleted_notifications(sender, instance, **kwargs):
    strategy = OfflineEventDeleted()
    _create_notifications(instance, strategy)


@receiver(pre_save, sender=OfflineEvent)
def handle_event_update_notifications(sender, instance, **kwargs):
    """Handle event update/reschedule notifications"""
    if instance.id is None:
        return  # Only handle updates, not creations

    strategy = OfflineEventUpdate()
    previous = OfflineEvent.objects.get(id=instance.id)
    # Check if important fields changed
    if previous and previous.date != instance.date:
        _create_notifications(instance, strategy)


@receiver(post_save, sender=OfflineEvent)
def handle_offline_event_notifications(sender, instance, created, **kwargs):
    """Handle offline event notifications"""
    if created and instance.project:
        strategy = OfflineEventCreated()
        _create_notifications(instance, strategy)


# Project Signals

# Initiator of idea should get moderator feedback


@receiver(post_save, sender=ParticipantInvite)
def handle_invite_received(sender, instance, created, **kwargs):
    if not created:
        return

    strategy = ProjectInvitationReceived()
    _create_notifications(instance, strategy)


@receiver(post_save, sender=ModeratorInvite)
def handle_moderator_invite_received(sender, instance, created, **kwargs):
    if not created:
        return

    strategy = ProjectModerationInvitationReceived()
    _create_notifications(instance, strategy)


@receiver(post_save, sender=Project)
def handle_project_created(sender, instance, created, **kwargs):
    if not created:
        return

    strategy = ProjectCreated()
    _create_notifications(instance, strategy)


@receiver(post_delete, sender=Project)
def handle_project_deleted(sender, instance, **kwargs):
    strategy = ProjectDeleted()
    _create_notifications(instance, strategy)
