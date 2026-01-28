from typing import List

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..constants import NOTIFICATION_MESSAGE_TEMPLATES
from ..models import NotificationType
from .base import BaseNotificationStrategy
from .project_strategies import ProjectNotificationStrategy

User = get_user_model()


class CommentHighlighted(BaseNotificationStrategy):
    """Strategy for notifications when a comment is highlighted"""

    def get_recipients(self, comment) -> List[User]:
        """Get the comment creator as potential recipient"""
        if comment.creator:
            return [comment.creator]
        return []

    def get_organisation(self, comment):
        return comment.project.organisation

    def create_notification_data(self, comment) -> dict:
        # Determine if there's a specific post URL or just project URL
        post_url = getattr(comment.content_object, "get_absolute_url", lambda: None)()
        cta_url = post_url if post_url else comment.project.get_absolute_url()
        cta_label = _("View post") if post_url else _("Visit the project")

        email_context = {
            "subject": _("A moderator highlighted your comment"),
            "headline": _("Project {project_name}").format(
                project_name=comment.project.name
            ),
            "cta_url": cta_url,
            "cta_label": cta_label,
            "reason": _(
                "This email was sent to {receiver_email}. You have received the e-mail because your contribution to the above project was highlighted by a moderator."
            ),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/moderator_highlighted_comment.en.email",
            # Template variables
            "project": comment.project.name,
            "project_url": comment.project.get_absolute_url(),
            "post_url": post_url,
        }

        return {
            "notification_type": NotificationType.MODERATOR_HIGHLIGHT,
            "message_template": NOTIFICATION_MESSAGE_TEMPLATES.MODERATOR_HIGHLIGHT,
            "context": {
                "project": comment.project.name,
                "project_url": comment.project.get_absolute_url(),
                "comment": comment.comment,
                "comment_url": comment.get_absolute_url(),
            },
            "email_context": email_context,
        }


class ProjectComment(ProjectNotificationStrategy):
    """Strategy for notifications when someone comments on project content"""

    def get_organisation(self, comment):
        return comment.project.organisation

    def get_recipients(self, comment) -> List[User]:
        """Get moderators and content creator as potential recipients"""
        recipients = set()

        # Add content creator if not the commenter
        if comment.content_object and hasattr(comment.content_object, "creator"):
            content_creator = comment.content_object.creator
            if content_creator != comment.creator:
                recipients.add(content_creator)

        return list(recipients)

    def create_notification_data(self, comment) -> dict:
        post_name = getattr(comment.content_object, "name", _("post"))

        email_context = {
            "subject": _("{commenter} commented on your post {post}").format(
                commenter=comment.creator.username, post=post_name
            ),
            "headline": _("New comment on your post"),
            "subheadline": comment.project.name,
            "cta_url": comment.content_object.get_absolute_url(),
            "cta_label": _("View post"),
            "reason": _(
                "This email was sent to {receiver_email} because someone commented on your content."
            ),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/comment_on_post.en.email",
            # Template variables
            "project_name": comment.project.name,
            "commenter_name": comment.creator.username,
            "post_name": post_name,
            "comment_text": comment.comment,
            "content_see_said": _("See what they said and join the discussion."),
        }

        return {
            "notification_type": NotificationType.COMMENT_ON_POST,
            "message_template": NOTIFICATION_MESSAGE_TEMPLATES.COMMENT_ON_POST,
            "context": {
                "user": comment.creator.username,
                "user_url": getattr(comment.creator, "get_absolute_url", lambda: "")(),
                "comment": comment.comment,
                "post_url": comment.content_object.get_absolute_url(),
                "post": post_name,
                "project": comment.project.name,
                "project_url": comment.project.get_absolute_url(),
            },
            "email_context": email_context,
        }


class CommentReply(BaseNotificationStrategy):
    """Handles notifications when someone replies to a user's comment"""

    def get_recipients(self, comment) -> List[User]:
        """Get parent comment creator as potential recipient"""
        parent_comment = self._get_parent_comment(comment)
        if parent_comment and parent_comment.creator:
            # Exclude the actor (comment creator) if they're replying to themselves
            if parent_comment.creator != comment.creator:
                return [parent_comment.creator]
        return []

    def _get_parent_comment(self, comment):
        """Get the parent comment if this is a reply"""
        return comment.parent_comment.first()

    def get_organisation(self, comment):
        return comment.project.organisation

    def create_notification_data(self, comment) -> dict:
        parent_comment = self._get_parent_comment(comment)

        email_context = {
            "subject": _("{commenter} replied to your comment").format(
                commenter=comment.creator.username
            ),
            "headline": _("New reply to your comment"),
            "subheadline": comment.project.name,
            "cta_url": comment.get_absolute_url(),
            "cta_label": _("View conversation"),
            "reason": _(
                "This email was sent to {receiver_email} because someone replied to your comment."
            ),
            # Content template
            "content_template": "a4_candy_notifications/emails/content/comment_reply.en.email",
            # Template variables
            "commenter_name": comment.creator.username,
            "comment_text": comment.comment,
            "parent_comment_text": parent_comment.comment if parent_comment else "",
            "content_join_conversation": _(
                "Join the conversation and continue the discussion."
            ),
        }

        return {
            "notification_type": NotificationType.COMMENT_REPLY,
            "message_template": NOTIFICATION_MESSAGE_TEMPLATES.COMMENT_REPLY,
            "context": {
                "user": comment.creator.username,
                "user_url": comment.creator.get_absolute_url(),
                "comment": "comment",
                "comment_url": comment.get_absolute_url(),
                "project": comment.project.name,
                "project_url": comment.project.get_absolute_url(),
            },
            "email_context": email_context,
        }
