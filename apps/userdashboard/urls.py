from django.urls import path
from django.urls import re_path

from . import views

urlpatterns = [
    path('overview/',
         views.UserDashboardOverviewView.as_view(),
         name='userdashboard-overview'),
    path('moderation/',
         views.UserDashboardModerationView.as_view(),
         name='userdashboard-moderation'),
    path('overview/activities/',
         views.UserDashboardActivitiesView.as_view(),
         name='userdashboard-activities'),
    path('overview/following/',
         views.UserDashboardFollowingView.as_view(),
         name='userdashboard-following'),
    re_path(r'^moderation/detail/(?P<slug>[-\w_]+)/$',
            views.UserDashboardModerationDetailView.as_view(),
            name='userdashboard-moderation-detail'),
]
