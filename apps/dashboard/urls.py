from django.conf.urls import include
from django.conf.urls import url

from adhocracy4.dashboard import components as a4dashboard_components
from adhocracy4.dashboard import views as a4dashborad_views
from apps.newsletters import views as newsletter_views
from apps.organisations import views as organisation_views

from . import views

app_name = 'a4dashboard'

urlpatterns = [
    url(r'^projects/(?P<project_slug>[-\w_]+)/blueprints/$',
        views.ModuleBlueprintListView.as_view(),
        name='module-blueprint-list'),
    url(r'^projects/(?P<project_slug>[-\w_]+)/blueprints/'
        r'(?P<blueprint_slug>[-\w_]+)/$',
        views.ModuleCreateView.as_view(),
        name='module-create'),
    url(r'^publish/module/(?P<module_slug>[-\w_]+)/$',
        views.ModulePublishView.as_view(),
        name='module-publish'),
    url(r'^delete/module/(?P<slug>[-\w_]+)/$',
        views.ModuleDeleteView.as_view(),
        name='module-delete'),
    url(r'^newsletters/create/$',
        newsletter_views.DashboardNewsletterCreateView.as_view(),
        name='newsletter-create'),
    url(r'^settings/$',
        organisation_views.DashboardOrganisationUpdateView.as_view(),
        name='organisation-settings'),
    url(r'^settings/legal-information$',
        organisation_views.DashboardLegalInformationUpdateView.as_view(),
        name='organisation-legal-information'),
]

# a4 dashboard urls without organisation slug
urlpatterns += [
    url(r'^organisations/projects/create$',
        views.ProjectCreateView.as_view(),
        name='project-create'),
    url(r'^organisations/projects/$',
        a4dashborad_views.ProjectListView.as_view(),
        name='project-list'),
    url(r'^projects/(?P<project_slug>[-\w_]+)/$',
        a4dashborad_views.ProjectUpdateView.as_view(),
        name='project-edit'),
    url(r'^publish/project/(?P<project_slug>[-\w_]+)/$',
        a4dashborad_views.ProjectPublishView.as_view(),
        name='project-publish'),
    url(r'', include(a4dashboard_components.get_urls())),
]
