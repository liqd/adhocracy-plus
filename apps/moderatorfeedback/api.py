from rest_framework import mixins
from rest_framework import viewsets

from adhocracy4.api.mixins import CommentMixin
from adhocracy4.api.permissions import ViewSetRulesPermission
from adhocracy4.comments_async import api as a4_api
from apps.moderatorfeedback.models import ModeratorCommentFeedback
from apps.moderatorfeedback.serializers import ModeratorCommentFeedbackSerializer
from apps.moderatorfeedback.serializers import ThreadListSerializer
from apps.moderatorfeedback.serializers import ThreadSerializer


class ModeratorCommentFeedbackViewSet(
    CommentMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ModeratorCommentFeedbackSerializer
    permission_classes = (ViewSetRulesPermission,)

    def get_permission_object(self):
        return self.comment

    def get_queryset(self):
        return ModeratorCommentFeedback.objects.filter(comment=self.comment)


class CommentWithFeedbackViewSet(a4_api.CommentViewSet):
    def get_serializer_class(self):
        if self.action == "list":
            return ThreadListSerializer
        return ThreadSerializer
