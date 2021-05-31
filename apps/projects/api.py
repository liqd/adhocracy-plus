from rest_framework import permissions
from rest_framework import viewsets

from adhocracy4.projects.models import Project

from .serializers import AppProjectSerializer


class AppProjectsViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = AppProjectSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return Project.objects.filter(
            is_draft=False,
            is_archived=False,
            is_app_accessible=True)
