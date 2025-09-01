from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic import View

from .forms import NotificationSettingsForm
from .models import Notification
from .models import NotificationSettings
from .models import NotificationType

class NotificationsDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view using expanded notification infrastructure."""

    template_name = "a4_candy_notifications/dashboard.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Translated strings
        context["dashboard_description"] = _(
            "All your important updates, all in one place — from reactions to your posts, to results from your saved searches, to the latest news from projects you follow. You can fine-tune what you get in Notification Settings in your account."
        )
        
        # Interactions section
        context["interactions_title"] = _("Interactions")
        context["interactions_description"] = _(
            "See all the ways you've connected and engaged with other members of the platform."
        )
        context["interactions_empty"] = _(
            "You haven't interacted with anyone yet. Start exploring and connect with other members!"
        )

        # Projects section
        context["projects_title"] = _("Followed Projects")
        context["projects_description"] = _(
            "Stay up to date with everything happening in the projects you follow — all the latest updates, right here."
        )
        context["projects_empty"] = _("No project updates yet")
        context["no_followed_projects"] = _(
            "You're not following any projects yet. Find projects that inspire you and click \"Follow\" on the project's header picture to see updates here."
        )

        # Moderation section
        context["moderation_title"] = _("Moderation & System")
        context["moderation_description"] = _(
            "Important notifications about content moderation, warnings, and system updates."
        )
        context["moderation_empty"] = _(
            "No moderation or system notifications at this time."
        )

        # Get all user notifications
        notifications = self.request.user.notifications.all().order_by("-created")

        # INTERACTIONS: User engagement notifications
        interactions = notifications.filter(
            Q(notification_type=NotificationType.USER_ENGAGEMENT) |
            Q(notification_type=NotificationType.MESSAGE_RECEIVED) |
            Q(notification_type=NotificationType.PROJECT_INVITATION) |
            Q(notification_type=NotificationType.COMMENT_REPLY) |
            Q(notification_type=NotificationType.CONTENT_REACTION)
        )

        # PROJECTS: Project-related notifications
        followed_projects = notifications.filter(
            Q(notification_type=NotificationType.PROJECT_UPDATE) |
            Q(notification_type=NotificationType.PROJECT_EVENT) |
            Q(notification_type=NotificationType.PROJECT_STARTED) |
            Q(notification_type=NotificationType.PHASE_STARTED) |
            Q(notification_type=NotificationType.PHASE_ENDED) |
            Q(notification_type=NotificationType.PROJECT_STATUS_CHANGE) |
            Q(notification_type=NotificationType.EVENT_ADDED) |
            Q(notification_type=NotificationType.EVENT_SOON) |
            Q(notification_type=NotificationType.EVENT_UPDATE) |
            Q(notification_type=NotificationType.EVENT_CANCELLED) |
            Q(notification_type=NotificationType.NEWSLETTER)
        )

        # MODERATION: Moderation and system notifications
        moderation = notifications.filter(
            Q(notification_type=NotificationType.MODERATOR_FEEDBACK) |
            Q(notification_type=NotificationType.MODERATOR_ACTION) |
            Q(notification_type=NotificationType.CONTENT_APPROVED) |
            Q(notification_type=NotificationType.CONTENT_REJECTED) |
            Q(notification_type=NotificationType.USER_WARNING) |
            Q(notification_type=NotificationType.CONTENT_FLAGGED) |
            Q(notification_type=NotificationType.SYSTEM)
        )

        # Unread counts
        context["interactions_unread_count"] = interactions.filter(read=False).count()
        context["projects_unread_count"] = followed_projects.filter(read=False).count()
        context["moderation_unread_count"] = moderation.filter(read=False).count()

        # Pagination
        context["interactions_page"] = self._paginate_queryset(
            interactions, page_param="interactions_page"
        )
        context["projects_page"] = self._paginate_queryset(
            followed_projects, page_param="projects_page"
        )
        context["moderation_page"] = self._paginate_queryset(
            moderation, page_param="moderation_page"
        )

        return context

    def _paginate_queryset(self, queryset, page_param):
        """Helper method to paginate querysets."""
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get(page_param, 1)
        page_obj = paginator.get_page(page_number)
        return page_obj


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
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.mark_as_read()
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
                    | Q(notification_type=NotificationType.PROJECT_EVENT)
                    | Q(notification_type=NotificationType.NEWSLETTER)
                )
            elif section == "interactions":
                notifications = notifications.filter(
                    Q(notification_type=NotificationType.USER_ENGAGEMENT)
                    | Q(notification_type=NotificationType.MODERATOR_FEEDBACK)
                    | Q(notification_type=NotificationType.SYSTEM)
                )
            pass

            notifications.update(read=True, read_at=timezone.now())
            messages.success(request, "All notifications marked as read")
        return redirect(request.META.get("HTTP_REFERER", "home"))
