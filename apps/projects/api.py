from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions
from rest_framework import viewsets

from adhocracy4.modules.models import Module
from adhocracy4.projects.enums import Access
from adhocracy4.projects.models import Project

from .serializers import AppModuleSerializer
from .serializers import AppProjectSerializer
from .serializers import ModerationProjectSerializer


# FIXME:rename it from AppProjectsViewSet to ProjectViewSet
class AppProjectsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AppProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "slug"

    def get_queryset(self):
        now = timezone.now()
        return Project.objects.filter(
            Q(access=Access.PUBLIC) | Q(access=Access.SEMIPUBLIC),
            Q(module__phase__start_date__lte=now)
            | Q(module__phase__start_date__gt=now),
            module__phase__end_date__gt=now,
            is_draft=False,
            is_archived=False,
            organisation__enable_geolocation=True,  # TODO: replace with a django filter later
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
