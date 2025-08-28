from django.urls import path

from . import views
from . import notification_views

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
    path(
        "notification-settings/",
        notification_views.NotificationSettingsView.as_view(),
        name="notification_settings",
    ),
    path("notifications/", notification_views.NotificationsView.as_view(), name="notifications"),
]
