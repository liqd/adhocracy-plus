from django.utils.translation import gettext as _

from .models import NotificationType

NOTIFICATION_SECTIONS = {
    "projects": [
        NotificationType.PROJECT_STARTED,
        NotificationType.PROJECT_COMPLETED,
        NotificationType.PROJECT_CREATED,
        NotificationType.PROJECT_DELETED,
        NotificationType.PHASE_STARTED,
        NotificationType.PHASE_ENDED,
        NotificationType.EVENT_ADDED,
        NotificationType.EVENT_SOON,
        NotificationType.EVENT_UPDATE,
        NotificationType.EVENT_CANCELLED,
        NotificationType.USER_CONTENT_CREATED,
    ],
    "interactions": [
        NotificationType.PROJECT_MODERATION_INVITATION,
        NotificationType.PROJECT_INVITATION,
        NotificationType.COMMENT_REPLY,
        NotificationType.COMMENT_ON_POST,
        NotificationType.MODERATOR_COMMENT_FEEDBACK,
        NotificationType.MODERATOR_HIGHLIGHT,
        NotificationType.MODERATOR_IDEA_FEEDBACK,
        NotificationType.MODERATOR_BLOCKED_COMMENT,
    ],
}


class NOTIFICATION_MESSAGE_TEMPLATES:
    MODERATOR_HIGHLIGHT = (
        "A moderator highlighted your comment '{comment}' in project {project}"
    )
    COMMENT_ON_POST = "{user} commented on your post {post}"
    COMMENT_REPLY = "{user} replied to your {comment}"
    EVENT_ADDED = "A new event '{event}' has been added to the project {project}"
    EVENT_CANCELLED = "The event '{event}' in project {project} has been cancelled"
    EVENT_SOON = "The event '{event}' in project {project} is starting on {event_date}"
    EVENT_UPDATE = "The event {event} in project {project} has been updated"
    MODERATOR_COMMENT_FEEDBACK = "A moderator gave feedback on your {comment}"
    MODERATOR_IDEA_FEEDBACK = "A moderator gave feedback on your idea {idea}"
    MODERATOR_PROPOSAL_FEEDBACK = (
        "A moderator gave feedback on your proposal {proposal}"
    )
    MODERATOR_BLOCKED_COMMENT = "Your comment was blocked in project {project_name}"
    PROJECT_STARTED = "The project {project} has begun."
    PROJECT_COMPLETED = "The project {project} has been completed."
    PROJECT_INVITATION = (
        "You have been invited to project {project}. Please check your email to accept."
    )
    PROJECT_MODERATION_INVITATION = "You have been invited to be a moderator of project {project_name}. View {invitation}"
    PROJECT_CREATED = "A new project {project} has been created."
    PROJECT_DELETED = "The project {project} has been deleted."
    USER_CONTENT_CREATED = (
        'A new {content_type} "{content}" has been created in project {project}.'
    )


# So that the translated strings stay in Transifex
class TRANSLATED_TEMPLATES:
    MODERATOR_HIGHLIGHT = _(NOTIFICATION_MESSAGE_TEMPLATES.MODERATOR_HIGHLIGHT)
    COMMENT_ON_POST = _(NOTIFICATION_MESSAGE_TEMPLATES.COMMENT_ON_POST)
    COMMENT_REPLY = _(NOTIFICATION_MESSAGE_TEMPLATES.COMMENT_REPLY)
    EVENT_ADDED = _(NOTIFICATION_MESSAGE_TEMPLATES.EVENT_ADDED)
    EVENT_CANCELLED = _(NOTIFICATION_MESSAGE_TEMPLATES.EVENT_CANCELLED)
    EVENT_SOON = _(NOTIFICATION_MESSAGE_TEMPLATES.EVENT_SOON)
    EVENT_UPDATE = _(NOTIFICATION_MESSAGE_TEMPLATES.EVENT_UPDATE)
    MODERATOR_COMMENT_FEEDBACK = _(
        NOTIFICATION_MESSAGE_TEMPLATES.MODERATOR_COMMENT_FEEDBACK
    )
    MODERATOR_IDEA_FEEDBACK = _(NOTIFICATION_MESSAGE_TEMPLATES.MODERATOR_IDEA_FEEDBACK)
    MODERATOR_PROPOSAL_FEEDBACK = _(
        NOTIFICATION_MESSAGE_TEMPLATES.MODERATOR_PROPOSAL_FEEDBACK
    )
    MODERATOR_BLOCKED_COMMENT = _(
        NOTIFICATION_MESSAGE_TEMPLATES.MODERATOR_BLOCKED_COMMENT
    )
    PROJECT_STARTED = _(NOTIFICATION_MESSAGE_TEMPLATES.PROJECT_STARTED)
    PROJECT_COMPLETED = _(NOTIFICATION_MESSAGE_TEMPLATES.PROJECT_COMPLETED)
    PROJECT_INVITATION = _(NOTIFICATION_MESSAGE_TEMPLATES.PROJECT_INVITATION)
    PROJECT_MODERATION_INVITATION = _(
        NOTIFICATION_MESSAGE_TEMPLATES.PROJECT_MODERATION_INVITATION
    )
    PROJECT_CREATED = _(NOTIFICATION_MESSAGE_TEMPLATES.PROJECT_CREATED)
    PROJECT_DELETED = _(NOTIFICATION_MESSAGE_TEMPLATES.PROJECT_DELETED)
    USER_CONTENT_CREATED = _(NOTIFICATION_MESSAGE_TEMPLATES.USER_CONTENT_CREATED)
