from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^overview/$',
        views.UserDashboardOverviewView.as_view(),
        name='userdashboard-overview'),
    url(r'^moderation/$',
        views.UserDashboardModerationView.as_view(),
        name='userdashboard-moderation'),
    url(r'^overview/activities/$',
        views.UserDashboardActivitiesView.as_view(),
        name='userdashboard-activities'),
    url(r'^overview/following/$',
        views.UserDashboardFollowingView.as_view(),
        name='userdashboard-following'),
    url(r'^moderation/detail/$',
        views.UserDashboardModerationDetailView.as_view(),
        name='userdashboard-moderation-detail'),
]
