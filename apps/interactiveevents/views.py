from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from adhocracy4.dashboard.mixins import DashboardBaseMixin
from adhocracy4.dashboard.mixins import DashboardComponentMixin
from adhocracy4.projects.mixins import DisplayProjectOrModuleMixin
from adhocracy4.projects.mixins import ProjectMixin

from . import forms
from . import models


class InteractiveEventModuleDetail(ProjectMixin,
                                   generic.TemplateView,
                                   DisplayProjectOrModuleMixin):
    template_name = \
        'a4_candy_interactive_events/module_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_fields'] = \
            models.ExtraFieldsInteractiveEvent.objects.filter(
                module=self.module).first()
        return context


class LiveQuestionModuleDetail(ProjectMixin,
                               generic.TemplateView,
                               DisplayProjectOrModuleMixin):
    template_name = \
        'a4_candy_interactive_events/livequestion_module_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_fields'] = \
            models.ExtraFieldsInteractiveEvent.objects.filter(
                module=self.module).first()
        return context


class LiveQuestionPresentationListView(ProjectMixin,
                                       PermissionRequiredMixin,
                                       generic.ListView):

    model = models.LiveQuestion
    permission_required = 'a4_candy_interactive_events.change_livequestion'

    def get_permission_object(self):
        return self.module

    def get_template_names(self):
        return ['a4_candy_interactive_events/present_list.html']

    def get_queryset(self):
        return super().get_queryset().filter(module=self.module)

    def get_full_url(self):
        request = self.request
        url = self.project.get_absolute_url()
        full_url = request.build_absolute_uri(url)
        return full_url


class ExtraFieldsDashboardView(ProjectMixin,
                               DashboardBaseMixin,
                               DashboardComponentMixin,
                               generic.UpdateView):
    model = models.ExtraFieldsInteractiveEvent
    template_name = \
        'a4_candy_interactive_events/extrafields_dashboard_form.html'
    permission_required = 'a4projects.change_project'
    form_class = forms.ExtraFieldsForm

    def get_permission_object(self):
        return self.project

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.module = self.module
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return models.ExtraFieldsInteractiveEvent.objects.\
            filter(module=self.module).first()
