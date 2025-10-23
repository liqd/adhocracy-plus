from django.contrib import auth
from django.urls import reverse
from wagtail.models import Site

from adhocracy4.emails.mixins import SyncEmailMixin
from apps.cms.settings.models import ImportantPages
from apps.users.emails import EmailAplus as Email

User = auth.get_user_model()


def _exclude_actor(receivers, actor):
    if not actor:
        return receivers

    if hasattr(receivers, "exclude"):
        return receivers.exclude(id=actor.id)

    return [receiver for receiver in receivers if not receiver == actor]


def _exclude_moderators(receivers, action):
    if hasattr(action, "project"):
        moderator_ids = action.project.moderators.values_list("id", flat=True)

        if hasattr(receivers, "exclude"):
            return receivers.exclude(id__in=moderator_ids)

        return [user for user in receivers if user.id not in moderator_ids]

    return receivers


def _exclude_notifications_disabled(receivers):
    if hasattr(receivers, "filter"):
        return receivers.filter(get_notifications=True)

    return [user for user in receivers if user.get_notifications]


class StrategyBasedEmail(SyncEmailMixin, Email):
    def get_receivers(self):
        recipient_ids = self.kwargs.get("strategy_recipient_ids")

        if recipient_ids:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            users = User.objects.filter(id__in=recipient_ids)
            return users

        return super().get_receivers()

    def get_organisation(self):
        if hasattr(self.object, "project") and self.object.project:
            return self.object.project.organisation
        return self.object.organisation

    def get_context(self):
        notification_data = self.kwargs.get("notification_data", {})
        notification_context = notification_data.get("context", {})
        return notification_context


class NotifyCreatorEmail(StrategyBasedEmail):
    template_name = "a4_candy_notifications/emails/notify_creator"


class NotifyCreatorOnModeratorFeedback(StrategyBasedEmail):
    template_name = "a4_candy_notifications/emails/notify_creator_on_moderator_feedback"

    def get_context(self):
        context = super().get_context()
        context["object"] = self.object
        return context


class NotifyCreatorOnModeratorBlocked(StrategyBasedEmail):
    template_name = "a4_candy_notifications/emails/notify_creator_on_moderator_blocked"

    def get_organisation(self):
        return self.object.project.organisation

    def get_netiquette_url(self):
        organisation = self.get_organisation()
        site = Site.objects.filter(is_default_site=True).first()
        important_pages = ImportantPages.for_site(site)
        if organisation.netiquette:
            return reverse(
                "organisation-netiquette",
                kwargs={"organisation_slug": organisation.slug},
            )
        elif (
            getattr(important_pages, "netiquette")
            and getattr(important_pages, "netiquette").live
        ):
            return getattr(important_pages, "netiquette").url
        else:
            return ""

    def get_discussion_url(self):
        if self.object.parent_comment.exists():
            return self.object.parent_comment.first().content_object.get_absolute_url()
        elif self.object.content_object.get_absolute_url():
            return self.object.content_object.get_absolute_url()
        else:
            return self.object.module.get_detail_url

    def get_context(self):
        context = super().get_context()
        context["module"] = self.object.module
        context["project"] = self.object.project
        context["netiquette_url"] = self.get_netiquette_url()
        context["discussion_url"] = self.get_discussion_url()
        return context


class NotifyCreatorOnModeratorCommentFeedback(StrategyBasedEmail):
    template_name = (
        "a4_candy_notifications/emails" "/notify_creator_on_moderator_comment_feedback"
    )

    def get_organisation(self):
        return self.object.project.organisation

    def get_context(self):
        context = super().get_context()
        context["project"] = self.object.project
        context["moderator_name"] = self.object.creator.username
        context["moderator_feedback"] = self.object.feedback_text
        context["comment_url"] = self.object.comment.get_absolute_url()
        return context


class NotifyModeratorsEmail(StrategyBasedEmail):
    template_name = "a4_candy_notifications/emails/notify_moderator"

    def get_organisation(self):
        return self.object.project.organisation


class NotifyInitiatorsOnProjectCreatedEmail(StrategyBasedEmail):
    template_name = "a4_candy_notifications/emails/notify_initiators_project_created"

    def get_organisation(self):
        return self.object.organisation


class NotifyInitiatorsOnProjectDeletedEmail(StrategyBasedEmail):
    template_name = "a4_candy_notifications/emails/notify_initiators_project_deleted"


class NotifyFollowersOnPhaseStartedEmail(StrategyBasedEmail):
    template_name = "a4_candy_notifications/emails" "/notify_followers_phase_started"

    def get_organisation(self):
        return self.object.project.organisation


class NotifyFollowersOnProjectStartedEmail(StrategyBasedEmail):
    template_name = "a4_candy_notifications/emails" "/notify_followers_project_started"


class NotifyFollowersOnProjectCompletedEmail(StrategyBasedEmail):
    template_name = (
        "a4_candy_notifications/emails" "/notify_followers_project_completed"
    )


class NotifyFollowersOnPhaseIsOverSoonEmail(StrategyBasedEmail):
    template_name = "a4_candy_notifications/emails" "/notify_followers_phase_over_soon"


class NotifyFollowersOnEventAddedEmail(StrategyBasedEmail):
    template_name = "a4_candy_notifications/emails" "/notify_followers_event_added"


class NotifyFollowersOnUpcomingEventEmail(StrategyBasedEmail):
    template_name = "a4_candy_notifications/emails" "/notify_followers_event_upcomming"
