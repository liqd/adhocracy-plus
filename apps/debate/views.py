from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from adhocracy4.dashboard import mixins
from adhocracy4.filters import views as filter_views
from adhocracy4.projects.mixins import DisplayProjectOrModuleMixin
from adhocracy4.projects.mixins import ProjectMixin
from apps.exports.views import DashboardExportView
from apps.ideas import views as idea_views

from . import filters
from . import forms
from . import models


class SubjectListView(idea_views.AbstractIdeaListView,
                      DisplayProjectOrModuleMixin):
    model = models.Subject
    filter_set = filters.SubjectFilterSet

    def get_queryset(self):
        return super().get_queryset()\
            .filter(module=self.module) \
            .annotate_comment_count()


class SubjectDetailView(idea_views.AbstractIdeaDetailView):
    model = models.Subject
    permission_required = 'a4_candy_debate.view_subject'


class SubjectListDashboardView(ProjectMixin,
                               mixins.DashboardBaseMixin,
                               mixins.DashboardComponentMixin,
                               filter_views.FilteredListView):
    model = models.Subject
    template_name = 'a4_candy_debate/subject_dashboard_list.html'
    permission_required = 'a4projects.change_project'
    filter_set = filters.SubjectCreateFilterSet

    def get_queryset(self):
        return super().get_queryset()\
            .filter(module=self.module) \
            .annotate_comment_count()

    def get_permission_object(self):
        return self.project


class SubjectCreateView(mixins.DashboardBaseMixin,
                        mixins.DashboardComponentMixin,
                        mixins.DashboardComponentFormSignalMixin,
                        idea_views.AbstractIdeaCreateView):
    model = models.Subject
    form_class = forms.SubjectForm
    permission_required = 'a4_candy_debate.add_subject'
    template_name = 'a4_candy_debate/subject_create_form.html'

    def get_success_url(self):
        return reverse(
            'a4dashboard:subject-list',
            kwargs={
                'organisation_slug': self.module.project.organisation.slug,
                'module_slug': self.module.slug
            })

    def get_permission_object(self):
        return self.module


class SubjectUpdateView(mixins.DashboardBaseMixin,
                        mixins.DashboardComponentMixin,
                        mixins.DashboardComponentFormSignalMixin,
                        idea_views.AbstractIdeaUpdateView):
    model = models.Subject
    form_class = forms.SubjectForm
    permission_required = 'a4_candy_debate.change_subject'
    template_name = 'a4_candy_debate/subject_update_form.html'

    @property
    def organisation(self):
        return self.project.organisation

    def get_success_url(self):
        return reverse(
            'a4dashboard:subject-list',
            kwargs={
                'organisation_slug': self.module.project.organisation.slug,
                'module_slug': self.module.slug
            })

    def get_permission_object(self):
        return self.get_object()


class SubjectDeleteView(mixins.DashboardBaseMixin,
                        mixins.DashboardComponentMixin,
                        mixins.DashboardComponentDeleteSignalMixin,
                        idea_views.AbstractIdeaDeleteView):
    model = models.Subject
    success_message = _('The subject has been deleted')
    permission_required = 'a4_candy_debate.change_subject'
    template_name = 'a4_candy_debate/subject_confirm_delete.html'

    @property
    def organisation(self):
        return self.project.organisation

    def get_success_url(self):
        return reverse(
            'a4dashboard:subject-list',
            kwargs={
                'organisation_slug': self.module.project.organisation.slug,
                'module_slug': self.module.slug
            })

    def get_permission_object(self):
        return self.get_object()


class SubjectDashboardExportView(DashboardExportView):
    template_name = 'a4_candy_exports/export_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export'] = reverse(
            'a4dashboard:subject-export',
            kwargs={
                'organisation_slug': self.module.project.organisation.slug,
                'module_slug': self.module.slug})
        context['comment_export'] = reverse(
            'a4dashboard:subject-comment-export',
            kwargs={
                'organisation_slug': self.module.project.organisation.slug,
                'module_slug': self.module.slug})
        return context
