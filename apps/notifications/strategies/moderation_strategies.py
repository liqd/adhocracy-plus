from typing import List

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..constants import EmailStrings
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
        email_context = {
            "subject": _("Feedback for your contribution on {site_name}"),
            "headline": _("Feedback for your contribution"),
            "subheadline": idea.project.name,
            "greeting": EmailStrings.GREETING,
            "cta_url": idea.get_absolute_url(),
            "cta_label": _("Check your contribution"),
            "reason": _(
                "This email was sent to {receiver_email}. You have received the e-mail because you added a contribution to the above project."
            ),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/moderator_feedback_on_post.en.email",
            # Template variables
            "project": idea.project,
            "organisation_name": idea.project.organisation.name,
            "moderator_status": getattr(idea, "moderator_status", None),
            "moderator_status_display": self._get_moderator_status_display(idea),
            "moderator_feedback": getattr(idea, "moderator_feedback", None),
        }

        return {
            "notification_type": NotificationType.MODERATOR_IDEA_FEEDBACK,
            "message_template": _("A moderator gave feedback on your idea {idea}"),
            "context": {
                "idea_url": idea.get_absolute_url(),
                "idea": idea.name,
                "project": idea.project.name,
                "organisation": idea.project.organisation.name,
            },
            "email_context": email_context,
        }

    def _get_moderator_status_display(self, idea):
        status = getattr(idea, "moderator_status", None)
        if status:
            status_map = {
                "approved": _("approved"),
                "rejected": _("rejected"),
                "reviewed": _("reviewed"),
            }
            return status_map.get(status, status)
        return ""


class ProposalFeedback(BaseNotificationStrategy):
    def get_recipients(self, proposal) -> List[User]:
        if proposal.creator:
            return [proposal.creator]
        return []

    def create_notification_data(self, proposal) -> dict:
        email_context = {
            "subject": _("Feedback for your contribution on {site_name}"),
            "headline": _("Feedback for your contribution"),
            "subheadline": proposal.project.name,
            "greeting": EmailStrings.GREETING,
            "cta_url": proposal.get_absolute_url(),
            "cta_label": _("Check your contribution"),
            "reason": _(
                "This email was sent to {receiver_email}. You have received the e-mail because you added a contribution to the above project."
            ),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/moderator_feedback_on_post.en.email",
            # Template variables
            "project": proposal.project,
            "organisation_name": proposal.project.organisation.name,
            "moderator_status": getattr(proposal, "moderator_status", None),
            "moderator_status_display": self._get_moderator_status_display(proposal),
            "moderator_feedback": getattr(proposal, "moderator_feedback", None),
        }

        return {
            "notification_type": NotificationType.MODERATOR_IDEA_FEEDBACK,
            "message_template": _(
                "A moderator gave feedback on your proposal {proposal}"
            ),
            "context": {
                "proposal_url": proposal.get_absolute_url(),
                "proposal": proposal.name,
                "project": proposal.project.name,
                "organisation": proposal.project.organisation.name,
            },
            "email_context": email_context,
        }

    def _get_moderator_status_display(self, idea):
        status = getattr(idea, "moderator_status", None)
        if status:
            status_map = {
                "approved": _("approved"),
                "rejected": _("rejected"),
                "reviewed": _("reviewed"),
            }
            return status_map.get(status, status)
        return ""


class CommentBlocked(BaseNotificationStrategy):
    """
    Strategy for notifications when a comment is blocked by a moderator.
    Provides context variables aligned with email template expectations.
    """

    def get_organisation(self, comment):
        return comment.project.organisation

    def get_recipients(self, comment) -> List[User]:
        """Notify the comment creator if they exist."""
        if comment.creator and comment.creator.get_notifications:
            return [comment.creator]
        return []

    def create_notification_data(self, comment) -> dict:
        project = comment.project

        email_context = {
            "subject": _("Your comment was moderated"),
            "headline": _("Your comment was moderated"),
            "subheadline": project.name,
            "greeting": _("Hello <strong>{receiver_name}</strong>,"),
            "cta_url": project.get_absolute_url(),
            "cta_label": _("View Project"),
            "reason": _("This email was sent to {receiver_email}."),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/moderator_blocked_comment.en.email",
            # Template variables
            "project_name": project.name,
            "comment_text": comment.comment,
            "netiquette_url": "/netiquette",  # You may want to make this configurable
            "organisation": project.organisation.name,
        }

        return {
            "notification_type": NotificationType.MODERATOR_BLOCKED_COMMENT,
            "message_template": "Your comment was moderated in project {project_name}",
            "context": {
                "project_name": project.name,
                "project_url": project.get_absolute_url(),
                "comment_text": comment.comment,
                "comment_url": comment.get_absolute_url(),
                "module_name": getattr(comment.module, "name", ""),
                "organisation": project.organisation.name,
            },
            "email_context": email_context,
        }
