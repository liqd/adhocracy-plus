from django.utils.translation import gettext_lazy as _

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
    NotificationType.MODERATOR_BLOCKED_COMMENT: emails.NotifyModeratorsEmail,
    NotificationType.EVENT_SOON: emails.NotifyFollowersOnUpcomingEventEmail,
    NotificationType.EVENT_CANCELLED: emails.NotifyFollowersOnEventDeletedEmail,
    NotificationType.EVENT_UPDATE: emails.NotifyFollowersOnEventUpdatedEmail,
    NotificationType.PROJECT_STARTED: emails.NotifyFollowersOnProjectStartedEmail,
    NotificationType.PROJECT_INVITATION: emails.NotifyFollowersOnProjectCompletedEmail,
    NotificationType.PROJECT_COMPLETED: emails.NotifyFollowersOnProjectCompletedEmail,
    NotificationType.COMMENT_ON_POST: emails.NotifyCreatorEmail,
    NotificationType.PROJECT_CREATED: emails.NotifyInitiatorsOnProjectCreatedEmail,
    NotificationType.PROJECT_DELETED: emails.NotifyInitiatorsOnProjectDeletedEmail,
    NotificationType.COMMENT_REPLY: emails.NotifyCreatorEmail,
    NotificationType.EVENT_ADDED: emails.NotifyFollowersOnEventAddedEmail,
    NotificationType.USER_CONTENT_CREATED: emails.NotifyModeratorsEmail,
}


class EmailStrings:
    # Greetings
    GREETING = _("Hello {receiver_name},")

    # CTA Labels
    CTA_VIEW_CONVERSATION = _("View conversation")
    CTA_VIEW_POST = _("View post")
    CTA_CHECK_CONTRIBUTION = _("Check your contribution")
    CTA_VISIT_PROJECT = _("Visit the project")
    CTA_SHOW_PROJECT = _("Show project")
    CTA_SHOW_EVENT = _("Show Event")
    CTA_JOIN_NOW = _("Join now")

    # Headlines
    HEADLINE_NEW_REPLY = _("New reply to your comment")
    HEADLINE_NEW_COMMENT = _("New comment on your post")
    HEADLINE_REACTION = _("Reaction to your contribution")
    HEADLINE_FEEDBACK = _("Feedback for your contribution")
    HEADLINE_EVENT = _("Event")
    HEADLINE_PARTICIPATION_ENDS = _("Participation ends soon!")
    HEADLINE_PROJECT_STARTS = _("Here we go!")

    # Content phrases
    CONTENT_JOIN_CONVERSATION = _("Join the conversation and continue the discussion.")
    CONTENT_SEE_SAID = _("See what they said and join the discussion.")
    CONTENT_ANSWER_PROMPT = _("Would you like to answer?")
    CONTENT_DO_ANSWER = _("Do you want to answer?")
    CONTENT_FURTHER_INFO = _("Further information can be found in the project.")


class ReasonStrings:
    # Comment/contribution related
    REASON_COMMENT_REPLY = _(
        "This email was sent to {receiver_email} because someone replied to your comment."
    )
    REASON_COMMENT_ON_POST = _(
        "This email was sent to {receiver_email} because someone commented on your content."
    )
    REASON_CONTRIBUTION_ADDED = _(
        "This email was sent to {receiver_email}. You have received the e-mail because you added a contribution to the above project."
    )

    # Project following related
    REASON_PROJECT_FOLLOWING = _(
        "This email was sent to {receiver_email}. You have received the e-mail because you are following the above project."
    )

    # Moderator/initiator related
    REASON_MODERATOR = _(
        "This email was sent to {receiver_email}. This email was sent to you because you are a moderator in the project."
    )
    REASON_INITIATOR = _(
        "This email was sent to {receiver_email}. This email was sent to you because you are an initiator of {organisation_name}."
    )


# subjects.py
from django.utils.translation import gettext_lazy as _


class SubjectStrings:
    SUBJECT_COMMENT_REPLY = _("{commenter} replied to your comment")
    SUBJECT_COMMENT_ON_POST = _("{commenter} commented on your post {post}")
    SUBJECT_REACTION = _("Reaction to your contribution in project {project_name}")
    SUBJECT_FEEDBACK = _("Feedback for your contribution on {site_name}")
    SUBJECT_MODERATED = _("Your comment was moderated")
    SUBJECT_HIGHLIGHTED = _("A moderator highlighted your comment")
    SUBJECT_NEW_EVENT = _("Event added to project {project}")
    SUBJECT_EVENT_CANCELLED = _("Event {event} in project {project} cancelled")
    SUBJECT_PARTICIPATION_ENDS = _("Participation ends soon for {project_name}")
    SUBJECT_PROJECT_STARTS = _("Here we go: {project_name} starts now!")
    SUBJECT_PROJECT_COMPLETED = _("{project_name} has completed.")
    SUBJECT_NEW_PROJECT = _("New project {project_name} on {site_name}")
