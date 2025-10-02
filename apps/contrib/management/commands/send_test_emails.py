from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.urls import reverse

from adhocracy4.actions.models import Action
from adhocracy4.actions.verbs import Verbs
from adhocracy4.comments.models import Comment
from adhocracy4.emails.mixins import SyncEmailMixin
from adhocracy4.projects.models import Project
from adhocracy4.reports import emails as reports_emails
from adhocracy4.reports.models import Report
from apps.account.emails import AccountDeletionEmail
from apps.cms.contacts.models import CustomFormSubmission
from apps.cms.contacts.models import FormPage
from apps.ideas.models import Idea
from apps.moderatorfeedback.models import ModeratorCommentFeedback
from apps.notifications import emails as notification_emails
from apps.offlineevents.models import OfflineEvent
from apps.projects import models as project_models
from apps.users.emails import EmailAplus as Email

User = get_user_model()


class TestEmail(SyncEmailMixin, Email):
    def get_organisation(self):
        project = getattr(self.object, "project", None)
        if project:
            return project.organisation

    def get_receivers(self):
        return self.kwargs["receiver"]

    def dispatch(self, object, *args, **kwargs):
        self.template_name = kwargs.pop("template_name")
        print(
            'Sending template: {} with object "{}"'.format(
                self.template_name, str(object)
            )
        )
        super().dispatch(object, *args, **kwargs)

    def get_context(self):
        context = super().get_context()
        context["project"] = getattr(self.object, "project", None)
        context["contact_email"] = settings.CONTACT_EMAIL
        return context


class Command(BaseCommand):
    help = "Send test emails to a registered user."

    def add_arguments(self, parser):
        parser.add_argument("email")

    """
    test missing for:   - newsletter_email
                        - notify_creator_on_moderator_feedback
    """

    def handle(self, *args, **options):
        self.user = User.objects.get(email=options["email"])

        self._send_notifications_create_idea()
        self._send_notifications_comment_idea()
        self._send_notifications_on_moderator_feedback()
        self._send_notification_event_upcoming()
        self._send_notification_phase()

        self._send_invitation_private_project()
        self._send_invitation_moderator()
        self._send_welcome_private_project()
        self._send_create_project()
        self._send_delete_project()

        self._send_report_mails()

        self._send_form_mail()

        self._send_allauth_email_confirmation()
        self._send_allauth_password_reset()
        self._send_allauth_unknown_account()
        self._send_allauth_account_already_exists()

        self._send_notification_blocked_comment()
        self._send_notification_moderator_comment_feedback()
        self._send_account_deleted_mail()

    def _send_notifications_create_idea(self):
        # Send notification for a newly created item
        action = (
            Action.objects.filter(
                verb=Verbs.ADD.value,
                obj_content_type=ContentType.objects.get_for_model(Idea),
            )
            .exclude(project=None)
            .first()
        )
        if not action:
            self.stderr.write("At least one idea is required")
            return

        self._send_notify_create_item(action)

    def _send_notifications_comment_idea(self):
        # Send notifications for a comment on a item
        action = (
            Action.objects.filter(
                verb=Verbs.ADD.value,
                obj_content_type=ContentType.objects.get_for_model(Comment),
                target_content_type=ContentType.objects.get_for_model(Idea),
            )
            .exclude(project=None)
            .first()
        )
        if not action:
            self.stderr.write("At least one idea with a comment is required")
            return

        self._send_notify_create_item(action)

    def _send_notify_create_item(self, action):
        TestEmail.send(
            action,
            receiver=[self.user],
            template_name=notification_emails.NotifyCreatorEmail.template_name,
        )

        TestEmail.send(
            action,
            receiver=[self.user],
            template_name=notification_emails.NotifyModeratorsEmail.template_name,
        )

    def _send_notifications_on_moderator_feedback(self):
        moderated_idea = Idea.objects.filter(
            moderator_feedback_text__isnull=False
        ).first()
        if not moderated_idea:
            self.stderr.write("At least one idea with moderator feedback is required")
            return

        TestEmail.send(
            moderated_idea,
            receiver=[self.user],
            template_name=notification_emails.NotifyCreatorOnModeratorFeedback.template_name,
        )

    def _send_notification_event_upcoming(self):
        offlineevent = OfflineEvent.objects.first()
        if not offlineevent:
            self.stderr.write("At least one offline event is required")
            return
        action = Action.objects.create(
            obj_content_type=ContentType.objects.get_for_model(OfflineEvent),
            obj=offlineevent,
            project=offlineevent.project,
            verb=Verbs.SCHEDULE,
        )

        TestEmail.send(
            action,
            receiver=[self.user],
            template_name=notification_emails.NotifyFollowersOnUpcomingEventEmail.template_name,
        )
        action.delete()

    def _send_notification_phase(self):
        action = Action.objects.filter(verb=Verbs.SCHEDULE.value).first()
        if not action:
            self.stderr.write("Schedule action is missing")
            return

        TestEmail.send(
            action,
            receiver=[self.user],
            template_name=notification_emails.NotifyFollowersOnPhaseIsOverSoonEmail.template_name,
        )

        TestEmail.send(
            action,
            receiver=[self.user],
            template_name=notification_emails.NotifyFollowersOnPhaseStartedEmail.template_name,
        )

    def _send_invitation_private_project(self):
        invite = project_models.ParticipantInvite.objects.first()
        if not invite:
            self.stderr.write("At least one participant request is required")
            return

        TestEmail.send(
            invite,
            receiver=[self.user],
            template_name="a4_candy_projects/emails/invite_participant",
        )

    def _send_invitation_moderator(self):
        invite = project_models.ModeratorInvite.objects.first()
        if not invite:
            self.stderr.write("At least one moderator request is required")
            return

        TestEmail.send(
            invite,
            receiver=[self.user],
            template_name="a4_candy_projects/emails/invite_moderator",
        )

    def _send_welcome_private_project(self):
        project = Project.objects.first()
        if not project:
            self.stderr.write("At least one project is required")
            return

        TestEmail.send(
            project,
            project=project,
            receiver=[self.user],
            template_name="a4_candy_projects/emails/welcome_participant",
        )

    def _send_create_project(self):
        project = Project.objects.first()
        if not project:
            self.stderr.write("At least one project is required")
            return
        TestEmail.send(
            project,
            project=project,
            creator=User.objects.first(),
            receiver=[self.user],
            template_name=(
                notification_emails.NotifyInitiatorsOnProjectCreatedEmail.template_name
            ),
        )

    def _send_delete_project(self):
        project = Project.objects.first()
        if not project:
            self.stderr.write("At least one project is required")
            return
        TestEmail.send(
            project,
            name=project.name,
            receiver=[self.user],
            template_name=(
                notification_emails.NotifyInitiatorsOnProjectDeletedEmail.template_name
            ),
        )

    def _send_report_mails(self):
        report = Report.objects.first()
        if not report:
            self.stderr.write("At least on report is required")
            return

        TestEmail.send(
            report,
            receiver=[self.user],
            template_name=reports_emails.ReportModeratorEmail.template_name,
        )

    def _send_form_mail(self):
        formpage = FormPage.objects.first()
        if not formpage:
            self.stderr.write("At least one emailformpage obj is required")
            return

        form_data = {
            "receive_copy": True,
        }
        submission = CustomFormSubmission.objects.create(
            page=formpage,
            form_data=form_data,
            email="me@you.net",
            message="This is an example message.",
            telephone_number="12345",
            name="your name",
        )

        TestEmail.send(
            submission,
            receiver=[self.user],
            template_name="a4_candy_cms_contacts/emails/answer_to_contact_form",
        )
        submission.delete()

    def _send_allauth_password_reset(self):
        context = {
            "current_site": "http://example.com/...",
            "user": self.user,
            "password_reset_url": "http://example.com/...",
            "request": None,
            "username": self.user.username,
        }

        TestEmail.send(
            self.user,
            receiver=[self.user],
            template_name="account/email/password_reset_key",
            **context
        )

    def _send_allauth_email_confirmation(self):
        context = {
            "user": self.user,
            "activate_url": "http://example.com/...",
            "current_site": "http://example.com/...",
            "key": "the1454key",
        }

        TestEmail.send(
            self.user,
            receiver=[self.user],
            template_name="account/email/email_confirmation_signup",
            **context
        )

        TestEmail.send(
            self.user,
            receiver=[self.user],
            template_name="account/email/email_confirmation",
            **context
        )

    def _send_allauth_unknown_account(self):
        context = {
            "user": self.user,
            "email": "user@example.com",
            "signup_url": "http://example.com/...",
            "current_site": "http://example.com/...",
        }

        TestEmail.send(
            self.user,
            receiver=[self.user],
            template_name="account/email/unknown_account",
            **context
        )

    def _send_allauth_account_already_exists(self):
        context = {
            "user": self.user,
            "email": "user@example.com",
            "password_reset_url": "http://example.com/...",
        }

        TestEmail.send(
            self.user,
            receiver=[self.user],
            template_name="account/email/account_already_exists",
            **context
        )

    def _send_notification_blocked_comment(self):
        # Send notification when comment is blocked
        comment = Comment.objects.first()
        if not comment:
            self.stderr.write("At least one comment is required")
            return
        netiquette_url = ""
        organisation = comment.project.organisation
        if organisation.netiquette:
            netiquette_url = reverse(
                "organisation-netiquette",
                kwargs={"organisation_slug": organisation.slug},
            )
        discussion_url = comment.module.get_detail_url
        if comment.parent_comment.exists():
            discussion_url = (
                comment.parent_comment.first().content_object.get_absolute_url()
            )
        elif comment.content_object.get_absolute_url():
            discussion_url = comment.content_object.get_absolute_url()
        TestEmail.send(
            comment,
            module=comment.module,
            project=comment.project,
            netiquette_url=netiquette_url,
            discussion_url=discussion_url,
            receiver=[self.user],
            template_name=notification_emails.NotifyCreatorOnModeratorBlocked.template_name,
        )

    def _send_notification_moderator_comment_feedback(self):
        # Send notification when moderator comment feedback is added
        feedback = ModeratorCommentFeedback.objects.first()
        if not feedback:
            self.stderr.write("At least one moderator comment feedback is required")
            return
        TestEmail.send(
            feedback,
            project=feedback.comment.project,
            moderator_name=feedback.creator.username,
            moderator_feedback=feedback.feedback_text,
            comment_url=feedback.comment.get_absolute_url(),
            receiver=[self.user],
            template_name=notification_emails.NotifyCreatorOnModeratorCommentFeedback.template_name,
        )

    def _send_account_deleted_mail(self):
        TestEmail.send(
            self.user,
            receiver=[self.user],
            template_name=AccountDeletionEmail.template_name,
        )
