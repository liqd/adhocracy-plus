from django.urls import path
from django.urls import re_path

from apps.notifications.views import MarkAllNotificationsAsReadView
from apps.notifications.views import MarkNotificationAsReadView
from apps.notifications.views import NotificationCountPartialView

from . import views

urlpatterns = [
    path(
        "overview/",
        views.UserDashboardOverviewView.as_view(),
        name="userdashboard-overview",
    ),
    path(
        "moderation/",
        views.UserDashboardModerationView.as_view(),
        name="userdashboard-moderation",
    ),
    path(
        "overview/notifications/",
        views.UserDashboardNotificationsView.as_view(),
        name="userdashboard-notifications",
    ),
    path(
        "overview/notifications/partial/",
        views.UserDashboardNotificationsPartialView.as_view(),
        name="userdashboard-notifications-partial",
    ),
    path(
        "overview/notifications/mark-as-read/<int:pk>/",
        MarkNotificationAsReadView.as_view(),
        name="mark_notification_as_read",
    ),
    path(
        "overview/notifications/mark-all-as-read/",
        MarkAllNotificationsAsReadView.as_view(),
        name="mark_all_notifications_as_read",
    ),
    path(
        "overview/notifications/count/",
        NotificationCountPartialView.as_view(),
        name="notification-count-partial",
    ),
    path(
        "overview/activities/",
        views.UserDashboardActivitiesView.as_view(),
        name="userdashboard-activities",
    ),
    path(
        "overview/following/",
        views.UserDashboardFollowingView.as_view(),
        name="userdashboard-following",
    ),
    re_path(
        r"^moderation/detail/(?P<slug>[-\w_]+)/$",
        views.UserDashboardModerationDetailView.as_view(),
        name="userdashboard-moderation-detail",
    ),
]
