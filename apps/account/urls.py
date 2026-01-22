from django.urls import path

from apps.notifications.views import NotificationSettingsView
from apps.notifications.views import TriggerAllNotificationTasksView

from . import views

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
        NotificationSettingsView.as_view(),
        name="account_notification_settings",
    ),
    path(
        "trigger-all-tasks/",
        TriggerAllNotificationTasksView.as_view(),
        name="trigger_all_notification_tasks",
    ),
]
