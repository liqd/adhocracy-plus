from rest_framework import viewsets

from apps.projects.serializers import ProjectSerializer

from . import helpers


class ModerationProjectsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        project_offensive_count = \
            {project: helpers.get_num_classifications(project)
             for project in list(self.request.user.project_moderator.all())}
        return sorted(project_offensive_count,
                      key=project_offensive_count.get,
                      reverse=True)
