from django.views import generic

from apps.users.models import User


class UserDashboardOverviewView(generic.base.ContextMixin,
                                generic.base.TemplateResponseMixin,
                                generic.base.View,
                                ):

    model = User
    template_name = 'a4_candy_userdashboard/userdashboard_overview.html'
    menu_item = 'overview'

    def get(self, request):
        response = self.render_to_response(self.get_context_data())
        return response


class UserDashboardModerationView(generic.base.ContextMixin,
                                  generic.base.TemplateResponseMixin,
                                  generic.base.View):

    model = User
    template_name = 'a4_candy_userdashboard/userdashboard_moderation.html'
    menu_item = 'moderation'

    def get(self, request):
        response = self.render_to_response(self.get_context_data())
        return response
