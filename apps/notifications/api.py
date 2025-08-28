from django.db.models import Count
from django.db.models import F
from django.db.models import IntegerField
from django.db.models import Q
from django.db.models import Value
from django.db.models import Window
from django.db.models.functions import RowNumber
from django.utils import timezone
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet

from adhocracy4.notifications.models import Notification
from adhocracy4.notifications.models import NotificationSettings

from .serializers import NotificationSerializer
from .serializers import NotificationSettingsSerializer


class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


class NotificationViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination

    def get_queryset(self):
        return (
            Notification.objects.filter(
                recipient=self.request.user,
            )
            .select_related(
                "action",
                "action__actor",
                "action__target_creator",
                "action__project",
                "action__obj_content_type",
                "action__target_content_type",
                "recipient",
            )
            .exclude(action__actor=self.request.user)
        )

    @action(methods=["get", "post"], detail=False)
    def interactions(self, request):
        """
        Annotate ratings query set to match non-rating notifications
        - `row_number` is used to match the number of columns per target object
        - `total_ratings` is used to match the amount of ratings per target object
        where target object can be a proposal, an idea, a comment.
        """
        base_qs = self.get_queryset().filter(action__target_creator=request.user)

        # Mark all notifications as read
        if request.method == "POST" and request.data.get("read", False):
            base_qs.filter(read=False).update(read=True, read_at=timezone.now())

        # Split into ratings and non-ratings
        rating_qs = base_qs.filter(action__obj_content_type__model="rating")
        non_rating_qs = base_qs.exclude(action__obj_content_type__model="rating")

        most_recent_ratings = rating_qs.annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("action__target_object_id")],
                order_by=F("action__timestamp").desc(),
            ),
            total_ratings=Window(
                expression=Count("id"),
                partition_by=[F("action__target_object_id")],
            ),
        ).filter(row_number=1)

        # Annotate non-rating notifications to match the same number of columns
        annotated_non_rating_qs = non_rating_qs.annotate(
            row_number=Value(None, output_field=IntegerField()),
            total_ratings=Value(None, output_field=IntegerField()),
        )

        # Combine querysets
        combined_qs = annotated_non_rating_qs.union(most_recent_ratings).order_by(
            "-action__timestamp"
        )

        unread_count = (
            non_rating_qs.filter(read=False).count()
            + most_recent_ratings.filter(read=False).count()
        )

        # Paginate and serialize
        page = self.paginate_queryset(combined_qs)
        serializer = self.get_serializer(page, many=True)
        response = self.get_paginated_response(serializer.data)
        response.data["unread_count"] = unread_count
        return response

    @action(methods=["get", "post"], detail=False)
    def followed_projects(self, request):
        qs = (
            self.get_queryset()
            .filter(
                Q(action__obj_content_type__model="offlineevent", action__verb="start")
                | (
                    Q(
                        action__obj_content_type__model="phase",
                        action__project__project_type="a4projects.Project",
                    )
                    & (Q(action__verb="start") | Q(action__verb="schedule"))
                ),
                recipient__follow__project=F("action__project"),
                recipient__follow__enabled=True,
            )
            .order_by("-action__timestamp")
        )

        # Mark all notifications as read
        if request.method == "POST" and request.data.get("read", False):
            qs.filter(read=False).update(read=True, read_at=timezone.now())

        unread_count = qs.filter(read=False).count()

        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        response = self.get_paginated_response(serializer.data)
        response.data["unread_count"] = unread_count
        return response


class NotificationSettingsViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    serializer_class = NotificationSettingsSerializer

    def get_queryset(self):
        return NotificationSettings.objects.filter(user=self.request.user)
