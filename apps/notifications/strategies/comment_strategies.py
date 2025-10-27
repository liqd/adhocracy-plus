from typing import List

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

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

    def create_notification_data(self, comment) -> dict:
        return {
            "notification_type": NotificationType.MODERATOR_HIGHLIGHT,
            "message_template": _(
                "A moderator highlighted your comment '{comment}' in project {project}"
            ),
            "context": {
                "project": comment.project.name,
                "project_url": comment.project.get_absolute_url(),
                "comment": comment.comment,
                "comment_url": comment.get_absolute_url(),
            },
        }


class ProjectComment(ProjectNotificationStrategy):
    """Strategy for notifications when someone comments on project content"""

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
        return {
            "notification_type": NotificationType.COMMENT_ON_POST,
            "message_template": _("{user} commented on your post {post}"),
            "context": {
                "user": comment.creator.username,
                "user_url": getattr(comment.creator, "get_absolute_url", lambda: "")(),
                "comment": comment.comment,
                "post_url": comment.content_object.get_absolute_url(),
                "post": getattr(comment.content_object, "name", _("post")),
                "project": comment.project.name,
                "project_url": comment.project.get_absolute_url(),
            },
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

    def create_notification_data(self, comment) -> dict:
        return {
            "notification_type": NotificationType.COMMENT_REPLY,
            "message_template": _("{user} replied to your {comment}"),
            "context": {
                "user": comment.creator.username,
                "user_url": getattr(comment.creator, "get_absolute_url", lambda: "")(),
                "comment": _("comment"),
                "comment_url": getattr(comment, "get_absolute_url", lambda: "")(),
                "project": comment.project.name,
                "project_url": comment.project.get_absolute_url(),
            },
        }
