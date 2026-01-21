from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from adhocracy4.actions.models import Action
from adhocracy4.comments.models import Comment
from adhocracy4.polls.models import Poll
from adhocracy4.projects.models import Project
from adhocracy4.rules import mixins as rules_mixins
from apps.documents.models import Chapter
from apps.documents.models import Paragraph
from apps.moderatorfeedback.models import ModeratorCommentFeedback
from apps.notifications.utils import get_notifications_by_section
from apps.organisations.models import Organisation
from apps.users.models import User


class UserDashboardBaseMixin(
    LoginRequiredMixin,
    generic.base.ContextMixin,
    generic.base.TemplateResponseMixin,
    generic.base.View,
):
    """
    Adds followed projects and organisations as properties.

    To be used in the user dashboard views, as they all need this info.
    """

    model = User

    def get(self, request):
        response = self.render_to_response(self.get_context_data())
        return response

    @property
    def organisations(self):
        return Organisation.objects.filter(
            project__follow__creator=self.request.user, project__follow__enabled=True
        ).distinct()

    @property
    def projects(self):
        projects = Project.objects.filter(
            follow__creator=self.request.user, follow__enabled=True
        )
        return projects


# user views
class UserDashboardOverviewView(UserDashboardBaseMixin):
    template_name = "a4_candy_userdashboard/userdashboard_overview.html"
    menu_item = "overview"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Translated strings
        context["dashboard_description"] = _(
            "All your important updates, all in one place — from reactions to your posts, to results from your saved searches, to the latest news from projects you follow. You can fine-tune what you get in Notification Settings in your account."
        )

        context["all_notifications_title"] = _("Notifications")

        # Interactions section
        context["interactions_title"] = _("Interactions")
        context["interactions_description"] = _(
            "See all the ways you've connected and engaged with other members of the platform."
        )
        context["interactions_empty"] = _(
            "You haven't interacted with anyone yet. Start exploring and connect with other members!"
        )

        # Projects section
        context["projects_title"] = _("Projects")
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

        # Get 10 user notifications
        notifications = self.request.user.notifications.all().order_by("-created")[:5]

        context["all_notifications"] = notifications
        context["is_preview_list"] = True
        return context

    def _paginate_queryset(self, queryset, page_param):
        """Helper method to paginate querysets."""
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get(page_param, 1)
        page_obj = paginator.get_page(page_number)
        return page_obj

    @property
    def projects_carousel(self):
        (
            sorted_active_projects,
            sorted_future_projects,
            sorted_past_projects,
        ) = self.request.user.get_projects_follow_list()
        projects = (
            list(sorted_active_projects)
            + list(sorted_future_projects)
            + list(sorted_past_projects)
        )[:8]

        return projects


class UserDashboardNotificationsBaseView(UserDashboardBaseMixin):
    """Base view with all shared notification logic"""

    paginate_by = 10

    def _get_notifications_context(self):
        """Shared context logic used by both full and partial views"""
        context = {}

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
        context["projects_title"] = _("Projects")
        context["projects_description"] = _(
            "Stay up to date with everything happening in the projects you follow — all the latest updates, right here."
        )
        context["projects_empty"] = _("No project updates yet")

        # Get all user notifications
        notifications = self.request.user.notifications.all().order_by("-created")

        # INTERACTIONS: User engagement notifications
        interactions = get_notifications_by_section(notifications, "interactions")

        # PROJECTS: Project-related notifications
        followed_projects = get_notifications_by_section(notifications, "projects")

        # Unread counts
        context["interactions_unread_count"] = interactions.filter(read=False).count()
        context["projects_unread_count"] = followed_projects.filter(read=False).count()

        # Pagination
        context["interactions_page"] = self._paginate_queryset(
            interactions, page_param="interactions_page"
        )
        context["projects_page"] = self._paginate_queryset(
            followed_projects, page_param="projects_page"
        )

        return context

    def _paginate_queryset(self, queryset, page_param):
        """Helper method to paginate querysets."""
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get(page_param, 1)
        return paginator.get_page(page_number)


class UserDashboardNotificationsView(UserDashboardNotificationsBaseView):
    """Main notifications page"""

    template_name = "a4_candy_userdashboard/userdashboard_notifications.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self._get_notifications_context())
        return context


class UserDashboardNotificationsPartialView(UserDashboardNotificationsBaseView):
    """HTMX partial for notifications content"""

    template_name = "a4_candy_notifications/_notifications_partial.html"

    def get(self, request, *args, **kwargs):
        context = self._get_notifications_context()

        # Check if a specific card was requested
        requested_card = request.GET.get("card")

        if requested_card == "interactions":
            # Return ONLY the interactions card
            return render(
                request,
                "a4_candy_notifications/_notification_card.html",
                self._get_interactions_context(context),
            )

        elif requested_card == "projects":
            # Return ONLY the projects card
            return render(
                request,
                "a4_candy_notifications/_notification_card.html",
                self._get_projects_context(context),
            )

        else:
            # No card specified = return full partial (both cards)
            return render(request, self.template_name, context)

    def _get_interactions_context(self, full_context):
        """Extract only interactions card context"""
        return {
            "section_id": "interactions",
            "title": full_context.get("interactions_title"),
            "description": full_context.get("interactions_description"),
            "unread_count": full_context.get("interactions_unread_count"),
            "notifications_list": full_context.get("interactions_page").object_list,
            "page_obj": full_context.get("interactions_page"),
            "param_name": "interactions_page",
            "pagination_required": full_context.get(
                "interactions_page"
            ).has_other_pages(),
            "is_preview_list": False,
            "empty_message": full_context.get("interactions_empty"),
            "empty_icon": "fa-comments",
        }

    def _get_projects_context(self, full_context):
        """Extract only projects card context"""
        return {
            "section_id": "projects",
            "title": full_context.get("projects_title"),
            "description": full_context.get("projects_description"),
            "unread_count": full_context.get("projects_unread_count"),
            "notifications_list": full_context.get("projects_page").object_list,
            "page_obj": full_context.get("projects_page"),
            "param_name": "projects_page",
            "pagination_required": full_context.get("projects_page").has_other_pages(),
            "is_preview_list": False,
            "empty_message": full_context.get("projects_empty"),
            "empty_icon": "fa-comments",
        }


class UserDashboardActivitiesView(UserDashboardBaseMixin):
    template_name = "a4_candy_userdashboard/userdashboard_activities.html"
    menu_item = "overview"

    @property
    def actions(self):
        """Return comment/feedback actions that are  on content the user created.

        Do not return actions on comments for polls and documents to not spam
        initiators.
        """
        user = self.request.user
        comment_actions = (
            Action.objects.filter(
                obj_content_type=ContentType.objects.get_for_model(Comment),
                verb="add",
                target_creator=user,
            )
            .exclude(
                target_content_type__in=[
                    ContentType.objects.get_for_model(Poll),
                    ContentType.objects.get_for_model(Chapter),
                    ContentType.objects.get_for_model(Paragraph),
                ]
            )
            .exclude(
                actor=user,
            )
            .select_related("actor", "project")
            .prefetch_related("obj", "target__creator")
        )

        filtered_comment_actions = [
            action for action in comment_actions if not action.obj.is_blocked
        ]
        feedback_actions = (
            Action.objects.filter(
                obj_content_type=ContentType.objects.get_for_model(
                    ModeratorCommentFeedback
                ),
                obj_comment_creator=user,
            )
            .exclude(actor=user)
            .select_related("project")
            .prefetch_related("obj__comment__creator")
        )

        return sorted(
            filtered_comment_actions + list(feedback_actions),
            key=lambda action: action.timestamp,
            reverse=True,
        )


class UserDashboardFollowingView(UserDashboardBaseMixin):
    template_name = "a4_candy_userdashboard/userdashboard_following.html"
    menu_item = "overview"


# moderation views
class UserDashboardModerationView(
    UserDashboardBaseMixin, rules_mixins.PermissionRequiredMixin
):
    template_name = "a4_candy_userdashboard/userdashboard_moderation.html"
    permission_required = "a4_candy_userdashboard.view_moderation_dashboard"
    menu_item = "moderation"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_api_url"] = reverse("moderationprojects-list")
        return context


class UserDashboardModerationDetailView(
    UserDashboardBaseMixin, rules_mixins.PermissionRequiredMixin
):
    template_name = "a4_candy_userdashboard/userdashboard_moderation_detail.html"
    permission_required = "a4_candy_userdashboard.change_moderation_comment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["moderation_comments_api_url"] = reverse(
            "moderationcomments-list", kwargs={"project_pk": self.project.pk}
        )
        return context

    def dispatch(self, request, *args, **kwargs):
        self.slug = kwargs.pop("slug")
        return super().dispatch(request, *args, **kwargs)

    @property
    def project(self):
        return get_object_or_404(Project, slug=self.slug)

    @property
    def project_url(self):
        return self.project.get_absolute_url()

    def get_permission_object(self):
        return self.project
