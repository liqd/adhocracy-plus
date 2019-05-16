from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<partner_slug>[-\w_]+)/$',
        views.PartnerView.as_view(),
        name='partner'),
    url(r'^(?P<partner_slug>[-\w_]+)/information/$',
        views.InformationView.as_view(),
        name='partner-information'),
    url(r'^(?P<partner_slug>[-\w_]+)/imprint/$',
        views.ImprintView.as_view(),
        name='partner-imprint'),
    url(r'^(?P<partner_slug>[-\w_]+)/settings/$',
        views.PartnerUpdateView.as_view(),
        name='partner-settings'),
]
