from typing import List

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..models import NotificationType
from .base import BaseNotificationStrategy

User = get_user_model()


class CommentFeedback(BaseNotificationStrategy):
    def get_in_app_recipients(self, feedback) -> List[User]:
        user_comment = feedback.comment
        if user_comment and user_comment.creator:
            return [user_comment.creator]
        return []

    def get_email_recipients(self, feedback) -> List[User]:
        user_comment = feedback.comment
        if user_comment and user_comment.creator:
            return [user_comment.creator]
        return []

    def create_notification_data(self, feedback) -> dict:
        user_comment = feedback.comment
        print(feedback)
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

    def get_in_app_recipients(self, idea) -> List[User]:
        recipients = set()
        if idea.creator:
            # TODO: Check user preferences
            recipients.add(idea.creator)

        return list(recipients)

    def get_email_recipients(self, idea) -> List[User]:
        return self.get_in_app_recipients(idea)

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

    def get_in_app_recipients(self, proposal) -> List[User]:
        recipients = set()
        if proposal.creator:
            # TODO: Check user preferences
            recipients.add(proposal.creator)

        return list(recipients)

    def get_email_recipients(self, proposal) -> List[User]:
        return self.get_in_app_recipients(proposal)

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

    def get_in_app_recipients(self, comment) -> List[User]:
        recipients = set()
        if comment.creator and hasattr(comment, "creator"):
            recipients.add(comment.creator)

        return list(recipients)

    def get_email_recipients(self, comment) -> List[User]:
        return self.get_in_app_recipients(comment)

    def create_notification_data(self, comment) -> dict:
        return {
            "notification_type": NotificationType.MODERATOR_BLOCKED_COMMENT,
            "message_template": _(
                "A moderator blocked your comment '{comment}' in project {project}"
            ),
            "context": {
                "project": comment.project.name if comment.project else "",
                "project_url": (
                    comment.project.get_absolute_url() if comment.project else "#"
                ),
                "comment": comment.comment,
                "comment_url": comment.get_absolute_url(),
            },
        }
