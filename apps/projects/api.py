from rest_framework import permissions
from rest_framework import viewsets

from adhocracy4.modules.models import Module
from adhocracy4.projects.models import Project

from .serializers import AppModuleSerializer
from .serializers import AppProjectSerializer
from .serializers import ModerationProjectSerializer


class AppProjectsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AppProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "slug"

    def get_queryset(self):
        return Project.objects.filter(
            is_draft=False, is_archived=False, is_app_accessible=True
        )


class AppModuleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AppModuleSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Module.objects.filter(is_draft=False, project__is_app_accessible=True)


class ModerationProjectsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ModerationProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.project_moderator.all().select_related("organisation")
