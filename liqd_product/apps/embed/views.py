from django.views import generic

from adhocracy4.projects import models as project_models
from liqd_product.apps.partners import set_partner
from meinberlin.apps.embed.views import EmbedView


class EmbedProjectView(generic.DetailView, EmbedView):
    model = project_models.Project
    template_name = "meinberlin_embed/embed.html"

    def get(self, request, *args, **kwargs):
        project = self.get_object()
        set_partner(project.organisation.partner)
        return super().get(request, *args, **kwargs)
