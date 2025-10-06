from django.contrib import auth
from django.urls import reverse
from wagtail.models import Site

from apps.cms.settings.models import ImportantPages
from apps.organisations.models import Organisation
from apps.projects import tasks
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


class NotifyCreatorEmail(Email):
    template_name = "a4_candy_notifications/emails/notify_creator"

    def get_organisation(self):
        return self.object.project.organisation

    def get_receivers(self):
        action = self.object
        if hasattr(action.target, "creator"):
            receivers = [action.target.creator]
            receivers = _exclude_notifications_disabled(receivers)
            receivers = _exclude_actor(receivers, action.actor)
            receivers = _exclude_moderators(receivers, action)
            return receivers
        return []


class NotifyCreatorOnModeratorFeedback(Email):
    template_name = "a4_candy_notifications/emails/notify_creator_on_moderator_feedback"

    def get_organisation(self):
        return self.object.project.organisation

    def get_receivers(self):
        receivers = [self.object.creator]
        receivers = _exclude_notifications_disabled(receivers)
        return receivers

    def get_context(self):
        context = super().get_context()
        context["object"] = self.object
        return context


class NotifyCreatorOnModeratorBlocked(Email):
    template_name = "a4_candy_notifications/emails/notify_creator_on_moderator_blocked"

    def get_organisation(self):
        return self.object.project.organisation

    def get_receivers(self):
        receivers = [self.object.creator]
        receivers = _exclude_notifications_disabled(receivers)
        return receivers

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


class NotifyCreatorOnModeratorCommentFeedback(Email):
    template_name = (
        "a4_candy_notifications/emails" "/notify_creator_on_moderator_comment_feedback"
    )

    def get_organisation(self):
        return self.object.project.organisation

    def get_receivers(self):
        receivers = [self.object.comment.creator]
        receivers = _exclude_notifications_disabled(receivers)
        return receivers

    def get_context(self):
        context = super().get_context()
        context["project"] = self.object.project
        context["moderator_name"] = self.object.creator.username
        context["moderator_feedback"] = self.object.feedback_text
        context["comment_url"] = self.object.comment.get_absolute_url()
        return context


class NotifyModeratorsEmail(Email):
    template_name = "a4_candy_notifications/emails/notify_moderator"

    def get_organisation(self):
        return self.object.project.organisation

    def get_receivers(self):
        action = self.object
        receivers = action.project.moderators.all()
        receivers = _exclude_actor(receivers, action.actor)
        receivers = _exclude_notifications_disabled(receivers)
        return receivers


class NotifyInitiatorsOnProjectCreatedEmail(Email):
    template_name = "a4_candy_notifications/emails/notify_initiators_project_created"

    def get_organisation(self):
        return self.object.organisation

    def get_receivers(self):
        project = self.object
        creator = project.creator
        receivers = project.organisation.initiators.all()
        receivers = _exclude_actor(receivers, creator)
        receivers = _exclude_notifications_disabled(receivers)
        return receivers

    def get_context(self):
        context = super().get_context()
        creator = User.objects.get(pk=self.kwargs["creator_pk"])
        context["creator"] = creator
        context["project"] = self.object
        return context


class NotifyInitiatorsOnProjectDeletedEmail(Email):
    template_name = "a4_candy_notifications/emails/notify_initiators_project_deleted"

    @classmethod
    def send_no_object(cls, object, *args, **kwargs):
        organisation = object.organisation
        object_dict = {
            "name": object.name,
            "initiators": list(
                organisation.initiators.all().distinct().values_list("email", flat=True)
            ),
            "organisation_id": organisation.id,
        }
        tasks.send_async_no_object.delay(
            cls.__module__, cls.__name__, object_dict, args, kwargs
        )
        return []

    def get_organisation(self):
        try:
            return Organisation.objects.get(id=self.object["organisation_id"])
        except Organisation.DoesNotExist:
            pass

    def get_receivers(self):
        return self.object["initiators"]

    def get_context(self):
        context = super().get_context()
        context["name"] = self.object["name"]
        return context


class NotifyFollowersOnPhaseStartedEmail(Email):
    template_name = "a4_candy_notifications/emails" "/notify_followers_phase_started"

    def get_organisation(self):
        return self.object.project.organisation

    def get_receivers(self):
        action = self.object
        receivers = User.objects.filter(
            follow__project=action.project,
            follow__enabled=True,
        )
        receivers = _exclude_notifications_disabled(receivers)
        return receivers


class NotifyFollowersOnPhaseIsOverSoonEmail(Email):
    template_name = "a4_candy_notifications/emails" "/notify_followers_phase_over_soon"

    def get_organisation(self):
        return self.object.project.organisation

    def get_receivers(self):
        action = self.object
        receivers = User.objects.filter(
            follow__project=action.project,
            follow__enabled=True,
        )
        receivers = _exclude_notifications_disabled(receivers)
        return receivers


class NotifyFollowersOnUpcomingEventEmail(Email):
    template_name = "a4_candy_notifications/emails" "/notify_followers_event_upcomming"

    def get_organisation(self):
        return self.object.project.organisation

    def get_receivers(self):
        action = self.object
        receivers = User.objects.filter(
            follow__project=action.project,
            follow__enabled=True,
        )
        receivers = _exclude_notifications_disabled(receivers)
        return receivers
