from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<year>\d{4})-(?P<pk>\d+)/$',
        views.SubjectDetailView.as_view(), name='subject-detail'),
    url(r'^(?P<slug>[-\w_]+)/$',
        views.SubjectDetailView.as_view(), name='subject-redirect'),
]
