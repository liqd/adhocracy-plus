from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^overview/$',
        views.UserDashboardOverviewView.as_view(),
        name='userdashboard-overview'),
    url(r'^moderation/$',
        views.UserDashboardModerationView.as_view(),
        name='userdashboard-moderation'),
]
