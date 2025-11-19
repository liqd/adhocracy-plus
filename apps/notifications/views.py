from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import UpdateView
from django.views.generic import View

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


class NotificationSettingsView(LoginRequiredMixin, UpdateView):
    model = NotificationSettings
    form_class = NotificationSettingsForm
    template_name = "a4_candy_notifications/settings.html"

    def get_object(self):
        """Get or create notification settings for the current user."""
        return NotificationSettings.get_for_user(self.request.user)

    def get_success_url(self):
        return reverse("account_notification_settings")


class TriggerAllNotificationTasksView(LoginRequiredMixin, View):
    """View to trigger all notification tasks (staff only)"""

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request):
        # Run all tasks
        send_recently_started_project_notifications.delay()
        send_recently_completed_project_notifications.delay()
        send_upcoming_event_notifications.delay()

        messages.success(request, "All notification tasks have been queued")
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
            print("RESPOONDING WITH TRIGGER")
            # Add HTMX trigger header to update the button
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

    def get(self, request, *args, **kwargs):
        unread_count = 0
        if request.user.is_authenticated:
            unread_count = Notification.objects.unread_count_for_user(request.user)

        return render(
            request,
            "a4_candy_notifications/_notifications_button_partial.html",
            {"user": request.user, "unread_count": unread_count},
        )
