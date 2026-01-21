from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from adhocracy4.dashboard.mixins import DashboardBaseMixin
from adhocracy4.dashboard.mixins import DashboardComponentMixin
from adhocracy4.projects.mixins import DisplayProjectOrModuleMixin
from adhocracy4.projects.mixins import ProjectMixin

from . import forms
from . import models


class ArpasModuleDetail(
    ProjectMixin, generic.TemplateView, DisplayProjectOrModuleMixin
):
    template_name = "a4_candy_arpas/module_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
