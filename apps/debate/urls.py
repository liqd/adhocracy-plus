from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        r"^(?P<year>\d{4})-(?P<pk>\d+)/$",
        views.SubjectDetailView.as_view(),
        name="subject-detail",
    ),
    re_path(
        r"^(?P<slug>[-\w_]+)/$",
        views.SubjectDetailView.as_view(),
        name="subject-redirect",
    ),
]
