from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from adhocracy4.rules import mixins as rules_mixins
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
