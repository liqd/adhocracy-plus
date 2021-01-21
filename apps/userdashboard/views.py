from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from adhocracy4.actions.models import Action
from adhocracy4.projects.models import Project
from adhocracy4.rules import mixins as rules_mixins
from apps.organisations.models import Organisation
from apps.users.models import User


class UserDashboardOverviewView(LoginRequiredMixin,
                                generic.base.ContextMixin,
                                generic.base.TemplateResponseMixin,
                                generic.base.View,
                                ):

    model = User
    template_name = 'a4_candy_userdashboard/userdashboard_overview.html'
    menu_item = 'overview'

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
                list(sorted_future_projects))[:9]


class UserDashboardModerationView(LoginRequiredMixin,
                                  rules_mixins.PermissionRequiredMixin,
                                  generic.base.ContextMixin,
                                  generic.base.TemplateResponseMixin,
                                  generic.base.View):

    model = User
    template_name = 'a4_candy_userdashboard/userdashboard_moderation.html'
    permission_required = 'a4_candy_userdashboard.view_moderation_dashboard'
    menu_item = 'moderation'

    def get(self, request):
        response = self.render_to_response(self.get_context_data())
        return response

    @property
    def organisations(self):
        return Organisation.objects.filter(
            project__follow__creator=self.request.user,
            project__follow__enabled=True
        ).distinct()


class UserDashboardActivitiesView(LoginRequiredMixin,
                                  generic.base.ContextMixin,
                                  generic.base.TemplateResponseMixin,
                                  generic.base.View,
                                  ):

    model = User
    template_name = 'a4_candy_userdashboard/userdashboard_activities.html'

    def get(self, request):
        response = self.render_to_response(self.get_context_data())
        return response

    @property
    def actions(self):
        return Action.objects.filter(
            actor=self.request.user,
        ).exclude_updates()


class UserDashboardFollowingView(LoginRequiredMixin,
                                 generic.base.ContextMixin,
                                 generic.base.TemplateResponseMixin,
                                 generic.base.View,
                                 ):

    model = User
    template_name = 'a4_candy_userdashboard/userdashboard_following.html'

    def get(self, request):
        response = self.render_to_response(self.get_context_data())
        return response

    @property
    def projects(self):
        return Project.objects.filter(follow__creator=self.request.user,
                                      follow__enabled=True)
