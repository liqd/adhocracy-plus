from django.urls import path

from .views import MarkNotificationAsReadView

app_name = "notifications"

urlpatterns = [
    path(
        "mark-as-read/<int:pk>/",
        MarkNotificationAsReadView.as_view(),
        name="mark_notification_as_read",
    ),
]
