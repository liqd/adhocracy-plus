import json
import logging

from django.conf import settings
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

from .algortihms import update_idea_choins_after_rating
from .models import Choin
from .models import ChoinEvent
from .models import Idea
from .models import IdeaChoin
from .serializers import ChoinSerializer
from .serializers import IdeaChoinSerializer

logger = logging.getLogger(__name__)


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
    def update_idea_choins_at_user_first_rating(self, request):
        """
        Should be called at the first time that a given user rates a given idea.
        """
        try:
            logger.info(request)
            value = request.data["value"]
            idea_id = request.data["ideaId"]
            user = request.user
            module = Idea.objects.get(pk=idea_id).module
            obj, created = Choin.objects.get_or_create(user=user, module=module)
            if (
                created
            ):  # Happens if this is the first time that the user rates any idea.
                message = f"You joined module '{module.name}' - project '{module.project.name}'"
                message_params = {
                    "module_name": module.name,
                    "project_name": module.project.name,
                }
                ChoinEvent.objects.create(
                    user=user,
                    module=module,
                    type="NEW",
                    content=message,
                    balance=0,
                    content_params=json.dumps(message_params),
                )
            choins = obj.choins
            logger.info(choins, user)
            if value == -1:  # NEGATIVE
                choins = 0
            update_idea_choins_after_rating(idea_id, choins)
            return Response(
                {"message": "choins are created"}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(e)
            return Response(
                {"message": "error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["POST"])
    def update_idea_choins_at_user_rating_update(self, request):
        """
        Should be called when a given user updates the rating to a given idea.
        """
        try:
            old_value = request.data["oldValue"]
            new_value = request.data["newValue"]
            logger.info("old rating: ", old_value, "new rating: ", new_value)
            idea_id = request.data["ideaId"]
            user = request.user
            module = Idea.objects.get(pk=idea_id).module
            obj, created = Choin.objects.get_or_create(user=user, module=module)
            if created:
                logger.info(
                    "Warning: New Choin created, although the user already rated"
                )
            choins = obj.choins
            if old_value == 1:  # If user remove their supporting
                choins *= -1
            elif new_value != 1:
                return
            update_idea_choins_after_rating(idea_id, choins)

            return Response(
                {"message": "choins are updated"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(e)
            return Response(
                {"message": "error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
