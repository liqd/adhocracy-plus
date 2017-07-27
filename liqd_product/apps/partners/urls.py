from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',
        views.PartnerView.as_view(),
        name='partner')
]
