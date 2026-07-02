from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from adhocracy4.polls.api import PollViewSet as BasePollViewSet
from adhocracy4.polls.models import Answer
from adhocracy4.polls.models import Vote
from apps.captcha.utils import verify_token


class PollViewSet(BasePollViewSet):
    def _get_total_participants(self, poll):
        auth_voters = set(
            Vote.objects.filter(choice__question__poll=poll)
            .exclude(creator=None)
            .values_list("creator_id", flat=True)
            .distinct()
        )
        auth_answerers = set(
            Answer.objects.filter(question__poll=poll)
            .exclude(creator=None)
            .values_list("creator_id", flat=True)
            .distinct()
        )
        anon_voters = set(
            Vote.objects.filter(choice__question__poll=poll)
            .exclude(content_id=None)
            .values_list("content_id", flat=True)
            .distinct()
        )
        anon_answerers = set(
            Answer.objects.filter(question__poll=poll)
            .exclude(content_id=None)
            .values_list("content_id", flat=True)
            .distinct()
        )
        return len(auth_voters | auth_answerers) + len(anon_voters | anon_answerers)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        if response.status_code == 200:
            poll = self.get_object()
            response.data["total_participants"] = self._get_total_participants(poll)
            response.data["module_name"] = poll.module.name
            response.data["module_description"] = poll.module.description or ""
        return response

    @action(detail=True, methods=["post"])
    def vote(self, request, pk=None):
        response = super().vote(request, pk)
        if response.status_code == 201:
            poll = self.get_object()
            response.data["total_participants"] = self._get_total_participants(poll)
        return response

    def check_captcha(self):
        # If CAPTCHA is globally disabled, do not enforce a check.
        if not getattr(settings, "CAPTCHA", False):
            return

        token = self.request.data.get("captcha", "")
        if not token:
            raise ValidationError(_("Please complete the captcha."))

        # Verify Prosopo token directly (no legacy Captcheck).
        if not verify_token(token):
            raise ValidationError(_("Captcha verification failed. Please try again."))
