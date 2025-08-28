from django.urls import reverse
from django.views import generic
from rest_framework.renderers import JSONRenderer
from rules.contrib.views import LoginRequiredMixin

from adhocracy4.actions.models import Action
from adhocracy4.notifications.models import NotificationSettings
from apps.notifications.serializers import NotificationSettingsSerializer


class NotificationsView(generic.TemplateView):
    model = Action
    template_name = "a4_candy_account/notifications.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notifications_api_url"] = reverse("notifications-list")
        context["interactions_api_url"] = reverse("notifications-interactions")
        context["followed_projects_api_url"] = reverse(
            "notifications-followed-projects"
        )
        return context


class NotificationSettingsView(LoginRequiredMixin, generic.TemplateView):
    template_name = "a4_candy_account/notification-settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        notification_settings, created = NotificationSettings.objects.get_or_create(
            user=user
        )
        context["notification_settings"] = notification_settings
        context["show_restricted"] = (
            user.project_moderator.exists() or len(user.organisations) > 0
        )

        data = NotificationSettingsSerializer(user.notification_settings).data
        context["data"] = JSONRenderer().render(data).decode("utf-8")
        context["api_url"] = reverse(
            "notification-settings-detail",
            kwargs={"pk": user.notification_settings.id},
        )
        return context
