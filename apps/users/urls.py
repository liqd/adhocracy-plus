from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^(?P<slug>[-\w _.@+-]+)/$", views.ProfileView.as_view(), name="profile"),
]
