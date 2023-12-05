from django.conf import settings
from django.db.models import F
from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from adhocracy4.api.mixins import ContentTypeMixin
from adhocracy4.api.permissions import ViewSetRulesPermission

from .models import Choin
from .models import Idea
from .models import IdeaChoin
from .serializers import ChoinSerializer
from .serializers import IdeaChoinSerializer


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
            POST="{app_label}.invest_{model}".format(
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


class IdeaChoinViewSet(viewsets.ModelViewSet):
    queryset = IdeaChoin.objects.all()
    serializer_class = IdeaChoinSerializer
    permission_classes = (IsAuthenticated,)
    # filter_backends = (filters.DjangoFilterBackend,)

    @action(detail=False, methods=["POST"])
    def add_choins_sum(self, request):
        try:
            print(request)
            value = request.data["value"]
            idea = request.data["ideaId"]
            user = request.user
            module = Idea.objects.get(pk=idea).module
            choins = Choin.objects.get(user=user, module=module).choins
            print(choins, user)
            if value == -1:  # NEGATIVE
                choins = 0
            obj = IdeaChoin.objects.update_or_create(
                idea=idea, defaults={"choins": F("choins") + choins}
            )
            print("ideachoin: ", obj)
            return Response(
                {"message": "choins are created"}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print(e)
            return Response(
                {"message": "error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["POST"])
    def update_choins_sum(self, request):
        try:
            print("hey")
            old_value = request.data["oldValue"]
            new_value = request.data["newValue"]
            idea = request.data["ideaId"]
            user = request.user
            module = Idea.objects.get(pk=idea).module
            choins = Choin.objects.get(user=user, module=module).choins

            if old_value == 1:  # POSITIVE
                choins *= -1
            elif new_value != 1:
                return

            obj = IdeaChoin.objects.update_or_create(
                idea=idea, defaults={"choins": F("choins") + choins}
            )
            print("ideachoin: ", obj)
            return Response(
                {"message": "choins are updated"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                {"message": "error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    """
    def perform_create(self, serializer):
        queryset = IdeaChoin.objects.filter(
            content_type_id=self.content_type.pk,
            creator=self.request.user,
            object_pk=self.content_object.pk,
        )
        if queryset.exists():
            raise ValidationError(queryset[0].pk)
        serializer.save(content_object=self.content_object, creator=self.request.user)

    @property
    def rules_method_map(self):
        return ViewSetRulesPermission.default_rules_method_map._replace(
            POST="{app_label}.invest_{model}".format(
                app_label=self.content_type.app_label, model=self.content_type.model
            )
        )

    def destroy(self, request, content_type, object_pk, pk=None):
        idea_choin = self.get_object()
        idea_choin.update(0)
        serializer = self.get_serializer(idea_choin)
        return Response(serializer.data)"""
