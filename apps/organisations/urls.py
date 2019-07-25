from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<organisation_slug>[-\w_]+)/$',
        views.OrganisationView.as_view(),
        name='organisation'),
    url(r'^(?P<organisation_slug>[-\w_]+)/information/$',
        views.InformationView.as_view(),
        name='organisation-information'),
    url(r'^(?P<organisation_slug>[-\w_]+)/imprint/$',
        views.ImprintView.as_view(),
        name='organisation-imprint'),
    url(r'^(?P<organisation_slug>[-\w_]+)/settings/$',
        views.OrganisationUpdateView.as_view(),
        name='organisation-settings'),
]
