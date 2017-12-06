from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<partner_slug>[-\w_]+)/$',
        views.PartnerView.as_view(),
        name='partner'),
    url(r'^(?P<partner_slug>[-\w_]+)/about/$',
        views.AboutView.as_view(),
        name='partner_about'),
    url(r'^(?P<partner_slug>[-\w_]+)/settings/$',
        views.PartnerUpdateView.as_view(),
        name='partner-settings'),
]
