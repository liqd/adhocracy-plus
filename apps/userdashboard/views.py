from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from adhocracy4.actions.models import Action
from adhocracy4.comments.models import Comment
from adhocracy4.polls.models import Poll
from adhocracy4.projects.models import Project
from adhocracy4.rules import mixins as rules_mixins
from apps.documents.models import Chapter
from apps.documents.models import Paragraph
from apps.moderatorfeedback.models import ModeratorCommentFeedback
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
            .exclude(actor=user)
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
            .select_related("project", "project__organisation")
            .prefetch_related("obj__comment__creator", "obj__comment__content_object")
        )

        return sorted(
            filtered_comment_actions + list(feedback_actions),
            key=lambda action: action.timestamp,
            reverse=True,
        )

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
