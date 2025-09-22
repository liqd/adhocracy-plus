from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import UpdateView
from django.views.generic import View

from .forms import NotificationSettingsForm
from .models import Notification
from .models import NotificationSettings
from .models import NotificationType


def is_safe_url(url):
    parsed = urlparse(url)
    return not parsed.netloc or parsed.netloc in settings.ALLOWED_HOSTS


class NotificationSettingsView(LoginRequiredMixin, UpdateView):
    """View for users to update their notification settings."""

    model = NotificationSettings
    form_class = NotificationSettingsForm
    template_name = "a4_candy_notifications/settings.html"

    def get_object(self):
        """Get or create notification settings for the current user."""
        obj, created = NotificationSettings.objects.get_or_create(
            user=self.request.user
        )
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse("account_notification_settings")


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


class MarkAllNotificationsAsReadView(LoginRequiredMixin, View):
    def post(self, request):
        section = request.POST.get("section", "")
        notifications = Notification.objects.filter(recipient=request.user, read=False)

        if section:
            if section == "projects":
                notifications = notifications.filter(
                    Q(notification_type=NotificationType.PROJECT_UPDATE)
                    | Q(notification_type=NotificationType.PROJECT_INVITATION)
                    | Q(notification_type=NotificationType.PROJECT_EVENT)
                    | Q(notification_type=NotificationType.PROJECT_STARTED)
                    | Q(notification_type=NotificationType.PROJECT_COMPLETED)
                    | Q(notification_type=NotificationType.PHASE_STARTED)
                    | Q(notification_type=NotificationType.PHASE_ENDED)
                    | Q(notification_type=NotificationType.PROJECT_STATUS_CHANGE)
                    | Q(notification_type=NotificationType.EVENT_ADDED)
                    | Q(notification_type=NotificationType.EVENT_SOON)
                    | Q(notification_type=NotificationType.EVENT_UPDATE)
                    | Q(notification_type=NotificationType.EVENT_CANCELLED)
                    | Q(notification_type=NotificationType.NEWSLETTER)
                )
            elif section == "interactions":
                notifications = notifications.filter(
                    Q(notification_type=NotificationType.USER_ENGAGEMENT)
                    | Q(notification_type=NotificationType.MESSAGE_RECEIVED)
                    | Q(notification_type=NotificationType.PROJECT_INVITATION)
                    | Q(notification_type=NotificationType.COMMENT_REPLY)
                    | Q(notification_type=NotificationType.MODERATOR_FEEDBACK)
                    | Q(notification_type=NotificationType.COMMENT_ON_POST)
                    | Q(notification_type=NotificationType.MODERATOR_HIGHLIGHT)
                    | Q(notification_type=NotificationType.MODERATOR_IDEA_FEEDBACK)
                    | Q(notification_type=NotificationType.MODERATOR_BLOCKED_COMMENT)
                )
            pass

            notifications.update(read=True, read_at=timezone.now())
            messages.success(request, "All notifications marked as read")
        return redirect(request.META.get("HTTP_REFERER", "home"))
