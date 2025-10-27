from typing import List

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..models import NotificationType
from .base import BaseNotificationStrategy

User = get_user_model()


class CommentFeedback(BaseNotificationStrategy):
    def get_recipients(self, feedback) -> List[User]:
        user_comment = feedback.comment
        if user_comment and user_comment.creator:
            return [user_comment.creator]
        return []

    def create_notification_data(self, feedback) -> dict:
        user_comment = feedback.comment
        return {
            "notification_type": NotificationType.MODERATOR_COMMENT_FEEDBACK,
            "message_template": _("A moderator gave feedback on your {comment}"),
            "context": {
                "moderator_feedback": feedback.feedback_text,
                "comment": _("comment"),
                "comment_url": user_comment.get_absolute_url(),
            },
        }


class IdeaFeedback(BaseNotificationStrategy):
    def get_recipients(self, idea) -> List[User]:
        if idea.creator:
            return [idea.creator]
        return []

    def create_notification_data(self, idea) -> dict:
        return {
            "notification_type": NotificationType.MODERATOR_IDEA_FEEDBACK,
            "message_template": _("A moderator gave feedback on your idea {idea}"),
            "context": {
                "idea_url": idea.get_absolute_url(),
                "idea": idea.name,
            },
        }


class ProposalFeedback(BaseNotificationStrategy):
    def get_recipients(self, proposal) -> List[User]:
        if proposal.creator:
            return [proposal.creator]
        return []

    def create_notification_data(self, proposal) -> dict:
        return {
            "notification_type": NotificationType.MODERATOR_IDEA_FEEDBACK,
            "message_template": _(
                "A moderator gave feedback on your proposal {proposal}"
            ),
            "context": {
                "proposal_url": proposal.get_absolute_url(),
                "proposal": proposal.name,
            },
        }


class CommentBlocked(BaseNotificationStrategy):
    """Strategy for notifications when a comment is blocked by a moderator"""

    def get_recipients(self, comment) -> List[User]:
        if comment.creator:
            return [comment.creator]
        return []

    def create_notification_data(self, comment) -> dict:
        return {
            "notification_type": NotificationType.MODERATOR_BLOCKED_COMMENT,
            "message_template": _(
                "A moderator blocked your comment '{comment}' in project {project}"
            ),
            "context": {
                "project": comment.project.name,
                "project_url": comment.project.get_absolute_url(),
                "comment": comment.comment,
                "comment_url": comment.get_absolute_url(),
            },
        }
