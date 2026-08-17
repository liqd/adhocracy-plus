from rest_framework import mixins
from rest_framework import viewsets

from adhocracy4.api.permissions import ViewSetRulesPermission

from .models import CustomFieldSettings
from .serializers import CustomFieldSettingsSerializer


class CustomFieldSettingsViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """ViewSet used to edit the custom fields from the dashboard."""

    queryset = CustomFieldSettings.objects.prefetch_related("fields__choices")
    serializer_class = CustomFieldSettingsSerializer
    permission_classes = (ViewSetRulesPermission,)

    def get_permission_object(self):
        settings = self.get_object()
        return settings.module
