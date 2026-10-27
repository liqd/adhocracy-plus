import logging
import re
from email.errors import HeaderParseError
from email.header import decode_header
from email.header import make_header

from bs4 import BeautifulSoup
from django.apps import apps
from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import generic

from adhocracy4 import transforms
from adhocracy4.dashboard import mixins as a4dashboard_mixins
from adhocracy4.follows.models import Follow
from adhocracy4.projects.models import Project
from adhocracy4.rules import mixins as rules_mixins

from . import models
from .emails import NewsletterEmail
from .emails import NewsletterPreviewEmail
from .forms import RestrictedNewsletterForm

Organisation = apps.get_model(settings.A4_ORGANISATIONS_MODEL)
User = auth.get_user_model()

logger = logging.getLogger(__name__)


class NewsletterCreateView(rules_mixins.PermissionRequiredMixin, generic.CreateView):
    model = models.Newsletter

    def _check_permission(self, organisation, user):
        return user.is_superuser or organisation.has_initiator(user)

    def form_valid(self, form):
        # Check if the current user is allowed to send to the selected org
        organisation = form.cleaned_data["organisation"]
        if not self._check_permission(organisation, self.request.user):
            raise PermissionDenied

        newsletter = form.save(commit=False)
        newsletter.creator = self.request.user
        newsletter.sent = timezone.now()
        newsletter.save()
        form.save_m2m()

        receivers = int(form.cleaned_data["receivers"])

        if receivers == models.PROJECT:
            participant_ids = Follow.objects.filter(
                project=form.cleaned_data["project"].pk, enabled=True
            ).values_list("creator", flat=True)

        else:
            participant_ids = []

        email = NewsletterEmail(
            newsletter=newsletter,
            organisation=organisation,
            participant_ids=list(participant_ids),
        )
        email.dispatch(newsletter)

        messages.success(
            self.request,
            _("Newsletter has been saved and " "will be sent to the recipients."),
        )

        return HttpResponseRedirect(self.get_success_url())


class DashboardNewsletterCreateView(
    a4dashboard_mixins.DashboardBaseMixin, NewsletterCreateView
):
    menu_item = "communication"
    form_class = RestrictedNewsletterForm
    permission_required = "a4projects.add_project"
    template_name = "a4_candy_newsletters/" "restricted_newsletter_dashboard_form.html"

    def get_email_kwargs(self):
        kwargs = {}
        kwargs.update({"organisation_pk": self.organisation.pk})
        return kwargs

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organisation"] = self.organisation
        kwargs["initial"]["receivers"] = models.PROJECT
        return kwargs

    def get_success_url(self):
        return reverse(
            "a4dashboard:newsletter-create",
            kwargs={"organisation_slug": self.organisation.slug},
        )

    def _group_permission(self, organisation, user):
        org_groups = organisation.groups.all()
        user_groups = user.groups.all()
        return (org_groups & user_groups).count() > 0

    def _check_permission(self, organisation, user):
        base_perms = super()._check_permission(organisation, user)
        return base_perms or self._group_permission(organisation, user)

    def get_permission_object(self):
        return self.organisation


class NewsletterPreviewMixin(a4dashboard_mixins.DashboardBaseMixin, generic.View):
    http_method_names = ["post"]
    permission_required = "a4projects.add_project"

    def get_permission_object(self):
        return self.organisation

    def get_newsletter(self):
        newsletter = models.Newsletter(
            creator=self.request.user,
            sender_name=self._clean_header(self.request.POST.get("sender_name", "")),
            sender=self._clean_sender(self.request.POST.get("sender", "")),
            subject=self._clean_header(self.request.POST.get("subject", "")),
            body=self.request.POST.get("body", ""),
            receivers=models.PROJECT,
            organisation=self.organisation,
        )

        project_id = self.request.POST.get("project", "")
        if project_id.isdigit():
            newsletter.project = Project.objects.filter(
                pk=project_id, organisation=self.organisation
            ).first()

        newsletter.body = transforms.clean_html_field(newsletter.body, "image-editor")
        return newsletter

    @staticmethod
    def _clean_header(value):
        return re.sub(r"[\r\n]+", " ", value).strip()

    @staticmethod
    def _clean_sender(value):
        value = value.strip()
        if not value:
            return ""
        try:
            validate_email(value)
        except ValidationError:
            return ""
        return value


class DashboardNewsletterPreviewView(NewsletterPreviewMixin):
    def post(self, request, *args, **kwargs):
        newsletter = self.get_newsletter()
        email = NewsletterEmail(newsletter, self.organisation, [])
        subject, _, email_html = email.render_for_receiver(request.user)
        reply_to = email.get_reply_to()

        context = {
            "subject": subject,
            "email_html": self._prepare_email_html(email_html),
            "recipient_count": self._get_recipient_count(newsletter),
            "from_email": self._decode_header(email.get_from_email()),
            "reply_to": self._decode_header(reply_to[0]) if reply_to else "",
            "preview_send_url": reverse(
                "a4dashboard:newsletter-preview-send",
                kwargs={"organisation_slug": self.organisation.slug},
            ),
        }
        return render(
            request,
            "a4_candy_newsletters/partials/newsletter_preview_modal.html",
            context,
        )

    def _get_recipient_count(self, newsletter):
        if not newsletter.project_id:
            return 0

        participant_ids = Follow.objects.filter(
            project_id=newsletter.project_id, enabled=True
        ).values_list("creator", flat=True)

        return (
            User.objects.filter(id__in=participant_ids)
            .filter(get_newsletters=True)
            .filter(is_active=True)
            .distinct()
            .count()
        )

    def _prepare_email_html(self, email_html):
        soup = BeautifulSoup(email_html, "html.parser")
        body = soup.body or soup
        logo_url = (
            self.organisation.logo.url
            if self.organisation.logo
            else static("images/email_logo.png")
        )

        for image in body.find_all("img"):
            if image.get("src") == "cid:logo":
                image["src"] = logo_url

        for link in body.find_all("a", href=True):
            link["target"] = "_blank"
            link["rel"] = "noopener noreferrer"

        return body.decode_contents()

    @staticmethod
    def _decode_header(value):
        try:
            return str(make_header(decode_header(value)))
        except (HeaderParseError, UnicodeError, ValueError):
            return value


class DashboardNewsletterPreviewSendView(NewsletterPreviewMixin):
    def post(self, request, *args, **kwargs):
        newsletter = self.get_newsletter()
        context = {}

        if not newsletter.subject.strip():
            context["error"] = _("Please add a subject before sending a test email.")
        elif not request.user.email:
            context["error"] = _("Your account has no email address.")
        else:
            email = NewsletterPreviewEmail(newsletter, self.organisation, request.user)
            try:
                email.dispatch(newsletter)
            except Exception:
                logger.exception("Failed to send newsletter test email")
                context["error"] = _(
                    "The test email could not be sent. Please try again."
                )
            else:
                context["success"] = True
                context["receiver_email"] = request.user.email

        return render(
            request,
            "a4_candy_newsletters/partials/newsletter_test_status.html",
            context,
        )
