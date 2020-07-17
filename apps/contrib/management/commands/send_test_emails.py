from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from adhocracy4.actions.models import Action
from adhocracy4.actions.verbs import Verbs
from adhocracy4.comments.models import Comment
from adhocracy4.emails.mixins import SyncEmailMixin
from adhocracy4.projects.models import Project
from adhocracy4.reports import emails as reports_emails
from adhocracy4.reports.models import Report
from apps.cms.contacts.models import CustomFormSubmission
from apps.cms.contacts.models import FormPage
from apps.ideas.models import Idea
from apps.notifications import emails as notification_emails
from apps.offlineevents.models import OfflineEvent
from apps.projects import emails as project_emails
from apps.projects import models as project_models
from apps.users.emails import EmailAplus as Email

User = get_user_model()


class TestEmail(SyncEmailMixin, Email):

    def get_organisation(self):
        project = getattr(self.object, 'project', None)
        if project:
            return project.organisation

    def get_receivers(self):
        return self.kwargs['receiver']

    def dispatch(self, object, *args, **kwargs):
        self.template_name = kwargs.pop('template_name')
        print('Sending template: {} with object "{}"'.format(
            self.template_name,
            str(object)))
        super().dispatch(object, *args, **kwargs)

    def get_context(self):
        context = super().get_context()
        context['project'] = getattr(self.object, 'project', None)
        context['contact_email'] = settings.CONTACT_EMAIL
        return context


class Command(BaseCommand):
    help = 'Send test emails to a registered user.'

    def add_arguments(self, parser):
        parser.add_argument('email')

    '''
    test missing for:   - newsletter_email
                        - notify_creator_on_moderator_feedback
    '''
    def handle(self, *args, **options):

        self.user = User.objects.get(email=options['email'])

        self._send_notifications_create_idea()
        self._send_notifications_comment_idea()
        self._send_notification_event_upcoming()
        self._send_notification_phase()
        self._send_notification_project_created()

        self._send_report_mails()

        self._send_allauth_email_confirmation()
        self._send_allauth_password_reset()

        self._send_invitation_private_project()
        self._send_invitation_moderator()
        self._send_delete_project()

        self._send_form_mail()

    def _send_notifications_create_idea(self):
        # Send notification for a newly created item
        action = Action.objects.filter(
            verb=Verbs.ADD.value,
            obj_content_type=ContentType.objects.get_for_model(Idea)
        ).exclude(project=None).first()
        if not action:
            self.stderr.write('At least one idea is required')
            return

        self._send_notify_create_item(action)

    def _send_notifications_comment_idea(self):
        # Send notifications for a comment on a item
        action = Action.objects.filter(
            verb=Verbs.ADD.value,
            obj_content_type=ContentType.objects.get_for_model(Comment),
            target_content_type=ContentType.objects.get_for_model(Idea)
        ).exclude(project=None).first()
        if not action:
            self.stderr.write('At least one idea with a comment is required')
            return

        self._send_notify_create_item(action)

    def _send_notify_create_item(self, action):
        TestEmail.send(
            action,
            receiver=[self.user],
            template_name=notification_emails.
            NotifyCreatorEmail.template_name)

        TestEmail.send(
            action,
            receiver=[self.user],
            template_name=notification_emails.
            NotifyModeratorsEmail.template_name)

    def _send_notification_event_upcoming(self):
        offlineevent = OfflineEvent.objects.first()
        if not offlineevent:
            self.stderr.write('At least one offline event is required')
            return
        action = Action.objects.create(
            obj_content_type=ContentType.objects.get_for_model(OfflineEvent),
            obj=offlineevent,
            project=offlineevent.project,
            verb=Verbs.SCHEDULE)

        TestEmail.send(
            action,
            receiver=[self.user],
            template_name=notification_emails.
            NotifyFollowersOnUpcommingEventEmail.template_name
        )
        action.delete()

    def _send_notification_phase(self):
        action = Action.objects.filter(
            verb=Verbs.SCHEDULE.value
        ).first()
        if not action:
            self.stderr.write('Schedule action is missing')
            return

        TestEmail.send(
            action,
            receiver=[self.user],
            template_name=notification_emails.
            NotifyFollowersOnPhaseIsOverSoonEmail.template_name
        )

        TestEmail.send(
            action,
            receiver=[self.user],
            template_name=notification_emails.
            NotifyFollowersOnPhaseStartedEmail.template_name
        )

    def _send_notification_project_created(self):
        project = Project.objects.first()
        TestEmail.send(
            project,
            project=project,
            creator=self.user,
            receiver=[self.user],
            template_name=notification_emails.
            NotifyInitiatorsOnProjectCreatedEmail.template_name
        )

    def _send_report_mails(self):
        report = Report.objects.first()
        if not report:
            self.stderr.write('At least on report is required')
            return

        TestEmail.send(
            report,
            receiver=[self.user],
            template_name=reports_emails.ReportModeratorEmail.template_name
        )

    def _send_allauth_password_reset(self):
        context = {"current_site": 'http://example.com/...',
                   "user": self.user,
                   "password_reset_url": 'http://example.com/...',
                   "request": None,
                   "username": self.user.username}

        TestEmail.send(self.user,
                       receiver=[self.user],
                       template_name='account/email/password_reset_key',
                       **context
                       )

    def _send_allauth_email_confirmation(self):
        context = {
            "user": self.user,
            "activate_url": 'http://example.com/...',
            "current_site": 'http://example.com/...',
            "key": 'the1454key',
        }

        TestEmail.send(
            self.user,
            receiver=[self.user],
            template_name='account/email/email_confirmation_signup',
            **context
        )

        TestEmail.send(
            self.user,
            receiver=[self.user],
            template_name='account/email/email_confirmation',
            **context
        )

    def _send_invitation_private_project(self):
        invite = project_models.ParticipantInvite.objects.first()
        if not invite:
            self.stderr.write('At least one participant request is required')
            return

        TestEmail.send(
            invite,
            receiver=[self.user],
            template_name='a4_candy_projects/emails/invite_participant'
        )

    def _send_invitation_moderator(self):
        invite = project_models.ModeratorInvite.objects.first()
        if not invite:
            self.stderr.write('At least one moderator request is required')
            return

        TestEmail.send(
            invite,
            receiver=[self.user],
            template_name='a4_candy_projects/emails/invite_moderator'
        )

    def _send_delete_project(self):
        project = Project.objects.first()
        if not project:
            self.stderr.write('At least one project is required')
            return
        TestEmail.send(
            project,
            name=project.name,
            organisation=project.organisation,
            receiver=[self.user],
            template_name=project_emails.DeleteProjectEmail.template_name
        )

    def _send_form_mail(self):
        formpage = FormPage.objects.first()
        if not formpage:
            self.stderr.write('At least one emailformpage obj is required')
            return

        submission = CustomFormSubmission.objects.create(
            page=formpage,
            email='me@you.net',
            message='This is an example message.',
            telephone_number='12345',
            name='your name'
        )

        TestEmail.send(
            submission,
            receiver=[self.user],
            template_name='a4_candy_cms_contacts/emails/answer_to_contact_form'
        )
        submission.delete()
