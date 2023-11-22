from django.conf import settings
from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from adhocracy4.api.mixins import ContentTypeMixin
from adhocracy4.api.permissions import ViewSetRulesPermission

from .models import Choin
from .serializers import ChoinSerializer


class ChoinViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    ContentTypeMixin,
    viewsets.GenericViewSet,
):
    queryset = Choin.objects.all()
    serializer_class = ChoinSerializer
    permission_classes = (ViewSetRulesPermission,)
    filter_backends = (filters.DjangoFilterBackend,)
    content_type_filter = settings.A4_RATEABLES

    def perform_create(self, serializer):
        queryset = Choin.objects.filter(
            content_type_id=self.content_type.pk,
            creator=self.request.user,
            object_pk=self.content_object.pk,
        )
        if queryset.exists():
            raise ValidationError(queryset[0].pk)
        serializer.save(content_object=self.content_object, creator=self.request.user)

    def get_permission_object(self):
        return self.content_object

    @property
    def rules_method_map(self):
        return ViewSetRulesPermission.default_rules_method_map._replace(
            POST="{app_label}.pay_{model}".format(
                app_label=self.content_type.app_label, model=self.content_type.model
            )
        )

    def destroy(self, request, content_type, object_pk, pk=None):
        """
        Sets value to zero
        NOTE: Choin is NOT deleted.
        """
        choin = self.get_object()
        choin.update(0)
        serializer = self.get_serializer(choin)
        return Response(serializer.data)
