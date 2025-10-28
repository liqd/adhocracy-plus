from . import emails
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

EMAIL_CLASS_MAPPING = {
    NotificationType.MODERATOR_HIGHLIGHT: emails.NotifyCreatorOnModeratorCommentHighlight,
    NotificationType.MODERATOR_COMMENT_FEEDBACK: emails.NotifyCreatorOnModeratorFeedback,
    NotificationType.MODERATOR_IDEA_FEEDBACK: emails.NotifyCreatorOnModeratorFeedback,
    NotificationType.MODERATOR_BLOCKED_COMMENT: emails.NotifyCreatorOnModeratorBlocked,
    NotificationType.EVENT_SOON: emails.NotifyFollowersOnUpcomingEventEmail,
    NotificationType.EVENT_CANCELLED: emails.NotifyFollowersOnEventDeletedEmail,
    NotificationType.EVENT_UPDATE: emails.NotifyFollowersOnEventUpdatedEmail,
    NotificationType.PROJECT_STARTED: emails.NotifyFollowersOnProjectStartedEmail,
    NotificationType.PROJECT_COMPLETED: emails.NotifyFollowersOnProjectCompletedEmail,
    NotificationType.COMMENT_ON_POST: emails.NotifyCreatorEmail,
    NotificationType.PROJECT_CREATED: emails.NotifyInitiatorsOnProjectCreatedEmail,
    NotificationType.PROJECT_DELETED: emails.NotifyInitiatorsOnProjectDeletedEmail,
    NotificationType.COMMENT_REPLY: emails.NotifyCreatorEmail,
    NotificationType.EVENT_ADDED: emails.NotifyFollowersOnEventAddedEmail,
    NotificationType.USER_CONTENT_CREATED: emails.NotifyModeratorsEmail,
}
