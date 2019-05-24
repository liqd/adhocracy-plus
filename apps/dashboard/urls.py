from django.conf.urls import url

from adhocracy4.dashboard.urls import urlpatterns as a4dashboard_urlpatterns
from apps.newsletters import views as newsletter_views

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
    url(r'^newsletters/(?P<organisation_slug>[-\w_]+)/create/$',
        newsletter_views.DashboardNewsletterCreateView.as_view(),
        name='newsletter-create'),
] + a4dashboard_urlpatterns
