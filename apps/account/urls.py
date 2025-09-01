from django.urls import path

from . import views
from apps.notifications.views import NotificationSettingsView, NotificationsDashboardView, MarkAllNotificationsAsReadView, MarkNotificationAsReadView

urlpatterns = [
    path("", views.AccountView.as_view(), name="account"),
    path("profile/", views.ProfileUpdateView.as_view(), name="account_profile"),
    path(
        "account_deletion/",
        views.AccountDeletionView.as_view(),
        name="account_deletion",
    ),
    path(
        "agreements/",
        views.OrganisationTermsOfUseUpdateView.as_view(),
        name="user_agreements",
    ),
    path("notifications/", NotificationsDashboardView.as_view(), name="account_notifications"),
    path("notifications-settings/", NotificationSettingsView.as_view(), name="account_notification_settings"),
    path('notifications/mark-as-read/<int:pk>/', MarkNotificationAsReadView.as_view(), name='mark_notification_as_read'),
    path('notifications/mark-all-as-read/', MarkAllNotificationsAsReadView.as_view(), name='mark_all_notifications_as_read'),
]
