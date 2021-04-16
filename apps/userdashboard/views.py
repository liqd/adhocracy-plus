from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from adhocracy4.actions.models import Action
from adhocracy4.projects.models import Project
from adhocracy4.rules import mixins as rules_mixins
from apps.organisations.models import Organisation
from apps.users.models import User


class UserDashboardBaseMixin(LoginRequiredMixin,
                             generic.base.ContextMixin,
                             generic.base.TemplateResponseMixin,
                             generic.base.View):
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
            project__follow__creator=self.request.user,
            project__follow__enabled=True
        ).distinct()

    @property
    def projects(self):
        return Project.objects.filter(follow__creator=self.request.user,
                                      follow__enabled=True)


# user views
class UserDashboardOverviewView(UserDashboardBaseMixin):

    template_name = 'a4_candy_userdashboard/userdashboard_overview.html'
    menu_item = 'overview'

    @property
    def actions(self):
        return Action.objects.filter(
            actor=self.request.user,
        ).exclude_updates()

    @property
    def projects_carousel(self):
        sorted_active_projects, sorted_future_projects, sorted_past_projects =\
            self.request.user.get_projects_follow_list()
        return (list(sorted_active_projects) +
                list(sorted_future_projects) +
                list(sorted_past_projects))[:8]


class UserDashboardActivitiesView(UserDashboardBaseMixin):

    template_name = 'a4_candy_userdashboard/userdashboard_activities.html'
    menu_item = 'overview'

    @property
    def actions(self):
        return Action.objects.filter(
            actor=self.request.user,
        ).exclude_updates()


class UserDashboardFollowingView(UserDashboardBaseMixin):

    template_name = 'a4_candy_userdashboard/userdashboard_following.html'
    menu_item = 'overview'


# moderation views
class UserDashboardModerationView(UserDashboardBaseMixin,
                                  rules_mixins.PermissionRequiredMixin):

    template_name = 'a4_candy_userdashboard/userdashboard_moderation.html'
    permission_required = 'a4_candy_userdashboard.view_moderation_dashboard'
    menu_item = 'moderation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project_api_url'] = reverse('moderationprojects-list')
        return context


class UserDashboardModerationDetailView(UserDashboardBaseMixin,
                                        rules_mixins.PermissionRequiredMixin):

    template_name = (
        'a4_candy_userdashboard/userdashboard_moderation_detail.html'
    )
    permission_required = 'a4_candy_classifications.view_userclassification'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aiclassification_api_url'] = \
            reverse('aiclassifications-list',
                    kwargs={'project_pk': self.project.pk})
        context['userclassification_api_url'] = \
            reverse('userclassifications-list',
                    kwargs={'project_pk': self.project.pk})
        return context

    def dispatch(self, request, *args, **kwargs):
        self.slug = kwargs.pop('slug')
        return super().dispatch(request, *args, **kwargs)

    @property
    def project(self):
        return get_object_or_404(
            Project,
            slug=self.slug
        )

    @property
    def project_url(self):
        return self.project.get_absolute_url()

    def get_permission_object(self):
        return self.project
