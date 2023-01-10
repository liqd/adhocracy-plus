from django.urls import include
from django.urls import path
from django.urls import re_path

from adhocracy4.dashboard import components as a4dashboard_components
from adhocracy4.dashboard import views as a4dashborad_views
from apps.newsletters import views as newsletter_views
from apps.organisations import views as organisation_views

from . import views

app_name = "a4dashboard"

urlpatterns = [
    re_path(
        r"^projects/(?P<project_slug>[-\w_]+)/blueprints/$",
        views.ModuleBlueprintListView.as_view(),
        name="module-blueprint-list",
    ),
    re_path(
        r"^projects/(?P<project_slug>[-\w_]+)/blueprints/"
        r"(?P<blueprint_slug>[-\w_]+)/$",
        views.ModuleCreateView.as_view(),
        name="module-create",
    ),
    re_path(
        r"^publish/module/(?P<module_slug>[-\w_]+)/$",
        views.ModulePublishView.as_view(),
        name="module-publish",
    ),
    re_path(
        r"^delete/module/(?P<slug>[-\w_]+)/$",
        views.ModuleDeleteView.as_view(),
        name="module-delete",
    ),
    path(
        "communication/newsletters/create/",
        newsletter_views.DashboardNewsletterCreateView.as_view(),
        name="newsletter-create",
    ),
    path(
        "settings/",
        organisation_views.DashboardOrganisationUpdateView.as_view(),
        name="organisation-settings",
    ),
    path(
        "settings/legal-information",
        organisation_views.DashboardLegalInformationUpdateView.as_view(),
        name="organisation-legal-information",
    ),
    path(
        "communication/content/create/",
        organisation_views.DashboardCommunicationProjectChoiceView.as_view(),
        name="communication-content",
    ),
    path(
        "communication/content/create/<slug:project_slug>/" "format/<int:format>/",
        organisation_views.DashboardCommunicationContentCreateView.as_view(),
        name="communication-content-create",
    ),
]

# a4 dashboard urls without organisation slug
urlpatterns += [
    path(
        "organisations/projects/create",
        views.ProjectCreateView.as_view(),
        name="project-create",
    ),
    path(
        "organisations/projects/",
        a4dashborad_views.ProjectListView.as_view(),
        name="project-list",
    ),
    re_path(
        r"^projects/(?P<project_slug>[-\w_]+)/$",
        a4dashborad_views.ProjectUpdateView.as_view(),
        name="project-edit",
    ),
    re_path(
        r"^publish/project/(?P<project_slug>[-\w_]+)/$",
        a4dashborad_views.ProjectPublishView.as_view(),
        name="project-publish",
    ),
    path("", include(a4dashboard_components.get_urls())),
]
