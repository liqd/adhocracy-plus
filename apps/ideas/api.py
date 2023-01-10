from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response

from adhocracy4.api.mixins import ModuleMixin
from adhocracy4.api.permissions import ViewSetRulesPermission

from .models import Idea
from .serializers import IdeaSerializer


class IdeaViewSet(
    ModuleMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):

    serializer_class = IdeaSerializer
    permission_classes = (ViewSetRulesPermission,)
    lookup_field = "pk"

    def get_permission_object(self):
        return self.module

    def get_queryset(self):
        ideas = (
            Idea.objects.filter(module=self.module)
            .annotate_comment_count()
            .annotate_positive_rating_count()
            .annotate_negative_rating_count()
            .order_by("created")
        )
        return ideas

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if "image_deleted" in request.data and request.data["image_deleted"]:
            if instance.image:
                instance.image.delete()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
