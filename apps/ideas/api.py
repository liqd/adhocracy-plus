from rest_framework import mixins
from rest_framework import viewsets

from adhocracy4.api.mixins import ModuleMixin
from adhocracy4.api.permissions import ViewSetRulesPermission

from .models import Idea
from .serializers import IdeaSerializer


class IdeaViewSet(ModuleMixin,
                  mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet,
                  ):

    serializer_class = IdeaSerializer
    permission_classes = (ViewSetRulesPermission,)
    lookup_field = 'pk'

    def get_permission_object(self):
        return self.module

    def get_queryset(self):
        ideas = Idea.objects\
            .filter(module=self.module) \
            .annotate_comment_count() \
            .annotate_positive_rating_count() \
            .annotate_negative_rating_count() \
            .order_by('created')
        return ideas
