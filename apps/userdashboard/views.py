from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views import generic

from adhocracy4.rules import mixins as rules_mixins
from adhocracy4.projects.enums import Access
from adhocracy4.projects.models import Project
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
        return Project.objects \
            .filter(follow__creator=self.request.user, follow__enabled=True) \
            .filter(Q(access=Access.PUBLIC) | Q(access=Access.SEMIPUBLIC))


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
