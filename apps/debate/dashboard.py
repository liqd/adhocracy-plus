from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from adhocracy4.dashboard import DashboardComponent
from adhocracy4.dashboard import components

from . import exports
from . import models
from . import views


class SubjectEditComponent(DashboardComponent):
    identifier = 'subject_edit'
    weight = 20
    label = _('Subjects')

    def is_effective(self, module):
        module_app = module.phases[0].content().app
        return module_app == 'a4_candy_debate'

    def get_progress(self, module):
        if models.Subject.objects.filter(module=module).exists():
            return 1, 1
        return 0, 1

    def get_base_url(self, module):
        return reverse('a4dashboard:subject-list', kwargs={
            'organisation_slug': module.project.organisation.slug,
            'module_slug': module.slug
        })

    def get_urls(self):
        return [
            (r'^subjects/module/(?P<module_slug>[-\w_]+)/$',
             views.SubjectListDashboardView.as_view(component=self),
             'subject-list'),
            (r'^subjects/create/module/(?P<module_slug>[-\w_]+)/$',
             views.SubjectCreateView.as_view(component=self),
             'subject-create'),
            (r'^subjects/(?P<year>\d{4})-(?P<pk>\d+)/update/$',
             views.SubjectUpdateView.as_view(component=self),
             'subject-update'),
            (r'^subjects/(?P<year>\d{4})-(?P<pk>\d+)/delete/$',
             views.SubjectDeleteView.as_view(component=self),
             'subject-delete')
        ]


components.register_module(SubjectEditComponent())


class ExportSubjectComponent(DashboardComponent):
    identifier = 'subject_export'
    weight = 50
    label = _('Export Excel')

    def is_effective(self, module):
        module_app = module.phases[0].content().app
        return (module_app == 'a4_candy_debate' and
                not module.project.is_draft)

    def get_progress(self, module):
        return 0, 0

    def get_base_url(self, module):
        return reverse('a4dashboard:subject-export-module', kwargs={
            'organisation_slug': module.project.organisation.slug,
            'module_slug': module.slug,
        })

    def get_urls(self):
        return [
            (r'^modules/(?P<module_slug>[-\w_]+)/export/subjects/$',
             views.SubjectDashboardExportView.as_view(),
             'subject-export-module'),
            (r'^modules/(?P<module_slug>[-\w_]+)/export/subjects/subjects/$',
             exports.SubjectExportView.as_view(),
             'subject-export'),
            (r'^modules/(?P<module_slug>[-\w_]+)/export/subjects/comments/$',
             exports.SubjectCommentExportView.as_view(),
             'subject-comment-export'),
        ]


components.register_module(ExportSubjectComponent())
