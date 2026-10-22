from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import UpdateView
from django.views.generic import View
from guest_user.functions import is_guest_user
from guest_user.mixins import RegularUserRequiredMixin

from adhocracy4.projects.models import Project
from apps.userdashboard.views import UserDashboardNotificationsBaseView

from .forms import NotificationSettingsForm
from .models import Notification
from .models import NotificationSettings
from .tasks import send_recently_completed_project_notifications
from .tasks import send_recently_started_project_notifications
from .tasks import send_upcoming_event_notifications
from .utils import get_notifications_by_section


def is_safe_url(url):
    parsed = urlparse(url)
    return not parsed.netloc or parsed.netloc in settings.ALLOWED_HOSTS


class NotificationSettingsView(
    LoginRequiredMixin, RegularUserRequiredMixin, UpdateView
):
    model = NotificationSettings
    form_class = NotificationSettingsForm
    template_name = "a4_candy_notifications/settings.html"

    def get_object(self):
        """Get or create notification settings for the current user."""
        return NotificationSettings.get_for_user(self.request.user)

    def get_success_url(self):
        return reverse("account_notification_settings")


class TriggerAllNotificationTasksView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View to trigger all notification tasks (staff only)."""

    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request):
        raw_slug = request.POST.get("project_slug", "").strip()
        project = Project.objects.filter(slug=raw_slug).first() if raw_slug else None
        if raw_slug and project is None:
            messages.error(request, f"No project found for slug {raw_slug!r}.")
            return redirect("account_notification_settings")

        project_id = project.pk if project else None

        # Run all tasks, optionally scoped to a single project
        send_recently_started_project_notifications.delay(project_id=project_id)
        send_recently_completed_project_notifications.delay(project_id=project_id)
        send_upcoming_event_notifications.delay(project_id=project_id)

        message = "All notification tasks have been queued"
        if project:
            message += f" for {project.name}"
        messages.success(request, message)
        return redirect("account_notification_settings")


class MarkAllNotificationsAsReadView(UserDashboardNotificationsBaseView):
    """Mark all notifications as read with HTMX support"""

    def post(self, request, *args, **kwargs):
        section = request.POST.get("section", "")
        notifications = Notification.objects.filter(recipient=request.user, read=False)

        if section:
            notifications = get_notifications_by_section(notifications, section)
            notifications.update(read=True, read_at=timezone.now())

        if request.headers.get("HX-Request"):
            context = self._get_notifications_context()
            response = render(
                request, "a4_candy_notifications/_notifications_partial.html", context
            )
            response["HX-Trigger"] = "updateNotificationCount"
            return response
        else:
            return redirect("userdashboard-notifications")


class MarkNotificationAsReadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        notification = get_object_or_404(
            Notification, id=kwargs["pk"], recipient=request.user
        )
        notification.mark_as_read()

        redirect_to = request.GET.get("redirect_to")
        if redirect_to and is_safe_url(redirect_to):
            return redirect(redirect_to)

        messages.success(request, "Notification marked as read")
        return redirect(request.META.get("HTTP_REFERER", "home"))


class NotificationCountPartialView(UserDashboardNotificationsBaseView):
    """HTMX partial for just the notification badge"""

    def dispatch(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            user = request.user
            if not user.is_authenticated or is_guest_user(user):
                return HttpResponse(status=204)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        unread_count = 0
        if request.user.is_authenticated:
            unread_count = Notification.objects.unread_count_for_user(request.user)

        return render(
            request,
            "a4_candy_notifications/_notifications_button_partial.html",
            {"user": request.user, "unread_count": unread_count},
        )
