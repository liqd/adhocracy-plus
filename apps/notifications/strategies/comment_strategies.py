from typing import List

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..models import NotificationSettings
from ..models import NotificationType
from .base import BaseNotificationStrategy
from .project_strategies import ProjectNotificationStrategy

User = get_user_model()


class CommentHighlighted(BaseNotificationStrategy):
    """Strategy for notifications when someone comments on a project"""

    def get_in_app_recipients(self, comment) -> List[User]:
        """Get recipients for in-app notifications (project author)"""
        recipients = set()
        if comment.creator and hasattr(comment, "creator"):
            recipients.add(comment.creator)

        return list(recipients)

    def get_email_recipients(self, comment) -> List[User]:
        """Get recipients for email notifications (project author)"""
        return self.get_in_app_recipients(comment)

    def create_notification_data(self, comment) -> dict:
        """Create notification data for project comments"""
        from django.utils.translation import gettext_lazy as _

        return {
            "notification_type": NotificationType.MODERATOR_HIGHLIGHT,
            "message_template": _(
                "A moderator highlighted your comment '{comment}' in project {project}"
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


class ProjectComment(ProjectNotificationStrategy):
    """Strategy for notifications when someone comments on a project"""

    def get_in_app_recipients(self, comment) -> List[User]:
        """Get recipients for in-app notifications (project author)"""
        recipients = set()
        moderators = self._get_project_moderators(comment.project)
        recipients.update(moderators)
        if comment.content_object and hasattr(comment.content_object, "creator"):
            # TODO: Check user preferences
            recipients.add(comment.content_object.creator)

        return list(recipients)

    def get_email_recipients(self, comment) -> List[User]:
        """Get recipients for email notifications (project author)"""
        return self.get_in_app_recipients(comment)

    # TODO: Check if content type can be added to message

    def create_notification_data(self, comment) -> dict:
        """Create notification data for project comments"""
        from django.utils.translation import gettext_lazy as _

        return {
            "notification_type": NotificationType.COMMENT_ON_POST,
            "message_template": _("{user} commented on your post {post}"),
            "context": {
                "user": comment.creator.username,
                "user_url": (
                    comment.creator.get_absolute_url()
                    if hasattr(comment.creator, "get_absolute_url")
                    else ""
                ),
                "comment": comment.comment,
                "post_url": comment.content_object.get_absolute_url(),
                "post": (
                    comment.content_object.name
                    if hasattr(comment.content_object, "name")
                    else ""
                ),  # TODO: Check how to handle this (Polls)
                "project": comment.project.name,
                "project_url": comment.project.get_absolute_url(),
            },
        }


class CommentReply(BaseNotificationStrategy):
    """Handles notifications when someone replies to a user's comment"""

    def _should_receive_comment_reply(self, user, channel):
        """Helper method to check if user should receive comment reply notifications"""
        settings = NotificationSettings.get_for_user(user)
        return settings.should_receive_notification(
            NotificationType.COMMENT_REPLY, channel
        )

    def get_in_app_recipients(self, comment) -> List[User]:
        parent_comment = self._get_parent_comment(comment)
        if parent_comment and parent_comment.creator:
            if self._should_receive_comment_reply(parent_comment.creator, "in_app"):
                return [parent_comment.creator]
        return []

    def get_email_recipients(self, comment) -> List[User]:
        parent_comment = self._get_parent_comment(comment)
        if parent_comment and parent_comment.creator:
            if self._should_receive_comment_reply(parent_comment.creator, "email"):
                return [parent_comment.creator]
        return []

    def _get_parent_comment(self, comment):
        """Get the parent comment if this is a reply"""
        parent_comments = comment.parent_comment.all()
        return parent_comments.first() if parent_comments.exists() else None

    def create_notification_data(self, comment) -> dict:
        comment_url = (
            comment.get_absolute_url() if hasattr(comment, "get_absolute_url") else ""
        )

        return {
            "notification_type": NotificationType.COMMENT_REPLY,
            "message_template": _("{user} replied to your {comment}"),
            "context": {
                "user": comment.creator.username,
                "user_url": (
                    comment.creator.get_absolute_url()
                    if hasattr(comment.creator, "get_absolute_url")
                    else ""
                ),
                "comment": _("comment"),
                "comment_url": comment_url,
            },
        }
