from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',
        views.PartnerView.as_view(),
        name='partner'),
    url(r'^about/$',
        views.AboutView.as_view(),
        name='partner_about'),
    url(r'^color/(?P<hex_value>[\w\d]+)/$',
        views.ColorView.as_view(),
        name='partner_color'),
]
