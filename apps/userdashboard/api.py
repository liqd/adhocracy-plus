# from django.db.models import Case
from django.db.models import Count

# from django.db.models import Exists
# from django.db.models import ExpressionWrapper
# from django.db.models import Max
# from django.db.models import OuterRef
# from django.db.models import Q
# from django.db.models import Value
# from django.db.models import When
# from django.db.models.fields import BooleanField
# from django.db.models.functions import Coalesce
# from django.db.models.functions import Greatest
from django.shortcuts import get_object_or_404

# from django_filters.rest_framework import BooleanFilter
from django_filters.rest_framework import DjangoFilterBackend

# from django_filters.rest_framework import FilterSet
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend

# from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from adhocracy4.api.permissions import ViewSetRulesPermission

# from adhocracy4.comments.models import Comment
from adhocracy4.projects.models import Project
from apps.notifications.emails import NotifyCreatorOnModeratorBlocked
from apps.projects import helpers

from . import serializers


class ClassificationFilterBackend(BaseFilterBackend):
    """Filter the comments for the classification categories.

    When a comment has both pending and archived notifications, only
    consider pending ones when filtering for categories.
    """

    def filter_queryset(self, request, queryset, view):
        """
        if ('classification' in request.GET
                and request.GET['classification'] != ''):
            classifi = request.GET['classification']
            return queryset.filter(
                Q(ai_classifications__is_pending=Case(
                    When(has_pending_notifications=True, then=Value(True)),
                    When(has_pending_notifications=False, then=Value(False))
                ),
                    ai_classifications__classification=classifi) |
                Q(user_classifications__is_pending=Case(
                    When(has_pending_notifications=True, then=Value(True)),
                    When(has_pending_notifications=False, then=Value(False))
                ),
                    user_classifications__classification=classifi)
            )
        """
        return queryset


'''
class ClassificationOrderingFilter(OrderingFilter):
    """Sort the comments by notification time and count.

    When a comment has both pending and archived notifications, only
    consider pending ones for the sorting.
    """

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if ordering:
            queryset = queryset.annotate(
                time_of_last_notification=Coalesce(
                    Greatest(
                        Max('ai_classifications__created'),
                        Max('user_classifications__created')
                    ),
                    Max('ai_classifications__created'),
                    Max('user_classifications__created')
                ))
            if 'new' in ordering:
                return queryset.order_by('-time_of_last_notification')
            elif 'old' in ordering:
                return queryset.order_by('time_of_last_notification')
            elif 'most' in ordering:
                queryset = queryset.annotate(
                    number_of_notifications=(Case(
                        When(has_pending_notifications=True, then=(
                            Count(
                                'ai_classifications',
                                filter=Q(ai_classifications__is_pending=True),
                                distinct=True
                            ) +
                            Count(
                                'user_classifications',
                                filter=Q(
                                    user_classifications__is_pending=True
                                ),
                                distinct=True
                            )
                        )),
                        When(has_pending_notifications=False, then=(
                            Count('ai_classifications', distinct=True)
                            + Count('user_classifications', distinct=True)
                        ))
                    )))
                return queryset.order_by('-number_of_notifications',
                                         '-time_of_last_notification')
        return queryset


class PendingNotificationsFilter(FilterSet):
    has_pending_notifications = BooleanFilter(
        field_name='has_pending_notifications')

    class Meta:
        model = Comment
        fields = ['has_pending_notifications']
'''


class ModerationCommentViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.ModerationCommentSerializer
    permission_classes = (ViewSetRulesPermission,)
    filter_backends = (
        DjangoFilterBackend,
        ClassificationFilterBackend,
    )
    # ClassificationOrderingFilter)
    # filterset_class = PendingNotificationsFilter
    # ordering_fields = ['new', 'old', 'most']
    # ordering = ['new']
    lookup_field = "pk"

    def dispatch(self, request, *args, **kwargs):
        self.project_pk = kwargs.get("project_pk", "")
        return super().dispatch(request, *args, **kwargs)

    @property
    def project(self):
        return get_object_or_404(Project, pk=self.project_pk)

    def get_permission_object(self):
        return self.project

    def get_queryset(self):
        all_comments_project = helpers.get_all_comments_project(self.project)
        return all_comments_project.annotate(
            num_reports=Count("reports", distinct=True)
        )

    def update(self, request, *args, **kwargs):
        if "is_blocked" in self.request.data and request.data["is_blocked"]:
            NotifyCreatorOnModeratorBlocked.send(self.get_object())
        return super().update(request, *args, **kwargs)

    @action(detail=True)
    def mark_read(self, request, **kwargs):
        comment = self.get_object()
        # FIXME: mark comment as read here
        serializer = self.get_serializer(comment)

        return Response(data=serializer.data, status=200)

    @action(detail=True)
    def mark_unread(self, request, **kwargs):
        comment = self.get_object()
        # FIXME: mark comment as unread here
        serializer = self.get_serializer(comment)

        return Response(data=serializer.data, status=200)

    @property
    def rules_method_map(self):
        return ViewSetRulesPermission.default_rules_method_map._replace(
            GET="a4_candy_userdashboard.view_moderation_comment",
            PUT="a4_candy_userdashboard.change_moderation_comment",
            PATCH="a4_candy_userdashboard.change_moderation_comment",
            OPTIONS="a4_candy_userdashboard.view_moderation_comment",
        )
