from rest_framework import viewsets

from apps.projects.serializers import ProjectSerializer


class ModerationProjectsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return list(self.request.user.project_moderator.all())
