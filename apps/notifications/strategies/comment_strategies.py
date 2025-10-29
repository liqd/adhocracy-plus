from typing import List

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..constants import EmailStrings
from ..constants import ReasonStrings
from ..constants import SubjectStrings
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
        cta_label = (
            EmailStrings.CTA_VIEW_POST if post_url else EmailStrings.CTA_VISIT_PROJECT
        )

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
            "email_context": {
                "email_subject": SubjectStrings.SUBJECT_HIGHLIGHTED.format(
                    project_name=comment.project.name
                ),
                "email_headline": _("Project {project_name}").format(
                    project_name=comment.project.name
                ),
                "email_greeting": EmailStrings.GREETING.format(
                    receiver_name=comment.creator.username
                ),
                "email_content": self._get_email_content(comment),
                "email_cta_url": cta_url,
                "email_cta_label": cta_label,
                "email_reason": ReasonStrings.REASON_CONTRIBUTION_ADDED.format(
                    receiver_email=comment.creator.email
                ),
                "project": comment.project.name,
                "project_url": comment.project.get_absolute_url(),
                "post_url": post_url,
            },
        }

    def _get_email_content(self, comment):
        """Generate the HTML content for the email"""
        """
<p>
A moderator highlighted your comment in the project.
</p>
"""


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

        return {
            "notification_type": NotificationType.COMMENT_ON_POST,
            "message_template": _("{user} commented on your post {post}"),
            "context": {
                "user": comment.creator.username,
                "user_url": getattr(comment.creator, "get_absolute_url", lambda: "")(),
                "comment": comment.comment,
                "post_url": comment.content_object.get_absolute_url(),
                "post": post_name,
                "project": comment.project.name,
                "project_url": comment.project.get_absolute_url(),
            },
            "email_context": {
                "email_subject": SubjectStrings.SUBJECT_COMMENT_ON_POST.format(
                    commenter=comment.creator.username, post=post_name
                ),
                "email_headline": EmailStrings.HEADLINE_NEW_COMMENT,
                "email_subheadline": comment.project.name,
                "email_greeting": EmailStrings.GREETING.format(
                    receiver_name=comment.creator.username
                ),
                "email_content": self._get_email_content(comment, post_name),
                "email_cta_url": comment.content_object.get_absolute_url(),
                "email_cta_label": EmailStrings.CTA_VIEW_POST,
                "email_reason": ReasonStrings.REASON_COMMENT_ON_POST.format(
                    receiver_email=comment.creator.email
                ),
                "project_name": comment.project.name,
                "commenter_name": comment.creator.username,
                "post_name": post_name,
                "comment_text": comment.comment,
                "post_url": comment.content_object.get_absolute_url(),
            },
        }

    def _get_email_content(self, comment, post_name):
        """Generate the HTML content for the email"""
        return f"""
<p>
<strong>{comment.creator.username}</strong> commented on your post "<strong>{post_name}</strong>".
</p>

<strong>Their comment:</strong>
<div style="margin: 0.5em 0; padding: 1em; background: #f8f9fa; border-left: 4px solid #2d40cc;">
    {comment.comment}
</div>

<p>
{EmailStrings.CONTENT_SEE_SAID}
</p>
"""


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
            "email_context": {
                "email_subject": SubjectStrings.SUBJECT_COMMENT_REPLY.format(
                    commenter=comment.creator.username
                ),
                "email_headline": EmailStrings.HEADLINE_NEW_REPLY,
                "email_subheadline": comment.project.name,
                "email_greeting": EmailStrings.GREETING.format(
                    receiver_name=comment.creator.username
                ),
                "email_content": self._get_email_content(comment, parent_comment),
                "email_cta_url": getattr(comment, "get_absolute_url", lambda: "")(),
                "email_cta_label": EmailStrings.CTA_VIEW_CONVERSATION,
                "email_reason": ReasonStrings.REASON_COMMENT_REPLY.format(
                    receiver_email=comment.creator.email
                ),
                "project_name": comment.project.name,
                "commenter_name": comment.creator.username,
                "comment_text": comment.comment,
                "parent_comment_text": parent_comment.comment if parent_comment else "",
            },
        }

    def _get_email_content(self, comment, parent_comment):
        """Generate the HTML content for the email"""
        return f"""
<p>
<strong>{comment.creator.username}</strong> replied to your comment in the project.
</p>

<strong>Your original comment:</strong>
<div style="margin: 0.5em 0; padding: 1em; background: #f8f9fa; border-left: 4px solid #417690;">
    {parent_comment.comment if parent_comment else ''}
</div>

<strong>Reply from {comment.creator.username}:</strong>
<div style="margin: 0.5em 0; padding: 1em; background: #f8f9fa; border-left: 4px solid #2d40cc;">
    {comment.comment}
</div>

<p>
{EmailStrings.CONTENT_JOIN_CONVERSATION}
</p>
"""
