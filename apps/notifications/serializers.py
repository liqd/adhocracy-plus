from django.utils import timezone
from rest_framework import serializers

from adhocracy4.actions.serializers import ActionSerializer
from adhocracy4.notifications.models import Notification
from adhocracy4.notifications.models import NotificationSettings


class NotificationSerializer(serializers.ModelSerializer):
    action = ActionSerializer(read_only=True)
    total_ratings = serializers.IntegerField(default=None)

    class Meta:
        model = Notification
        fields = (
            "total_ratings",  # field from annotated QS
            "action",
            "read",
            "read_at",
            "id",
        )
        read_only_fields = ("action", "total_ratings", "read_at")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Remove `total_ratings` if it’s `None` (only shows for aggregated ratings)
        if "total_ratings" in data and data.get("total_ratings") is None:
            del data["total_ratings"]
        return data

    def save(self, **kwargs):
        if "read" in self.validated_data:
            return super().save(**kwargs, read_at=timezone.now())
        return super().save(**kwargs)


class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        exclude = (
            "user",
            "id",
        )
