from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView, UpdateView, View
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from .models import Notification, NotificationSettings
from .forms import NotificationSettingsForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import NotificationType

class NotificationsDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view using existing notification infrastructure."""
    template_name = 'a4_candy_notifications/dashboard.html'
    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context = super().get_context_data(**kwargs)
    
        context['dashboard_description'] = _("All your important updates, all in one place — from reactions to your posts, to results from your saved searches, to the latest news from projects you follow. You can fine-tune what you get in Notification Settings in your account.")
        context['interactions_title'] = _("Interactions")
        context['interactions_description'] = _("See all the ways you've connected and engaged with other members of the platform.")
        context['interactions_empty'] = _("You haven't interacted with anyone yet. Start exploring and connect with other members!")
        
        context['projects_title'] = _("Followed Projects") 
        context['projects_description'] = _("Stay up to date with everything happening in the projects you follow — all the latest updates, right here.")
        context['projects_empty'] = _("No project updates yet")
        context['no_followed_projects'] = _("You're not following any projects yet. Find projects that inspire you and click \"Follow\" on the project's header picture to see updates here.")
        
        
        notifications = self.request.user.notifications.all().order_by('-created')
        
        interactions = notifications.filter(
            Q(notification_type=NotificationType.USER_ENGAGEMENT) |
            Q(notification_type=NotificationType.MODERATOR_FEEDBACK) |
            Q(notification_type=NotificationType.SYSTEM)
        )
        
        followed_projects = notifications.filter(
            Q(notification_type=NotificationType.PROJECT_UPDATE) |
            Q(notification_type=NotificationType.PROJECT_EVENT) |
            Q(notification_type=NotificationType.NEWSLETTER)
        )
        
        context['interactions_unread_count'] = interactions.filter(read=False).count()
        context['projects_unread_count'] = followed_projects.filter(read=False).count()

        context['interactions_page'] = self._paginate_queryset(
            interactions, 
            page_param='interactions_page'
        )
        context['projects_page'] = self._paginate_queryset(
            followed_projects,
            page_param='projects_page'
        )
        
        return context
    
    def _paginate_queryset(self, queryset, page_param='page'):
        """Paginate queryset with custom page parameter."""
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get(page_param, 1)
        return paginator.get_page(page_number)

class NotificationSettingsView(LoginRequiredMixin, UpdateView):
    """View for users to update their notification settings."""
    model = NotificationSettings
    form_class = NotificationSettingsForm
    template_name = 'a4_candy_notifications/settings.html'
    success_url = 'notification-settings'
    
    def get_object(self):
        """Get or create notification settings for the current user."""
        obj, created = NotificationSettings.objects.get_or_create(
            user=self.request.user
        )
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_groups'] = self.get_form().get_field_groups()
        return context

    def get_success_url(self):
        """Ensure we redirect to the correct URL."""
        return 'notification-settings'

class MarkNotificationAsReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.mark_as_read()
        messages.success(request, 'Notification marked as read')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

class MarkAllNotificationsAsReadView(LoginRequiredMixin, View):
    def post(self, request):
        section = request.POST.get('section', '')
        notifications = Notification.objects.filter(recipient=request.user, read=False)
        
        if section:
            if section == 'projects':
                notifications = notifications.filter(
                    Q(notification_type=NotificationType.PROJECT_UPDATE) |
                    Q(notification_type=NotificationType.PROJECT_EVENT) |
                    Q(notification_type=NotificationType.NEWSLETTER)
                )
            elif section == 'interactions':
                notifications = notifications.filter(
                    Q(notification_type=NotificationType.USER_ENGAGEMENT) |
                    Q(notification_type=NotificationType.MODERATOR_FEEDBACK) |
                    Q(notification_type=NotificationType.SYSTEM)
                )
            pass
            
            notifications.update(read=True, read_at=timezone.now())
            messages.success(request, 'All notifications marked as read')
        return redirect(request.META.get('HTTP_REFERER', 'home'))