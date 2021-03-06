from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt

from adhocracy4.projects import models as project_models


class EmbedView(generic.View):
    @xframe_options_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(EmbedView, self).dispatch(request, *args, **kwargs)


class EmbedProjectView(generic.DetailView, EmbedView):
    model = project_models.Project
    template_name = "a4_candy_embed/embed.html"


class EmbedLoginClose(generic.base.TemplateView):
    template_name = "a4_candy_embed/login_popup_close.html"
