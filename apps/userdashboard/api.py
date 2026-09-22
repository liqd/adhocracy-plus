from django.db.models import CharField
from django.db.models import Count
from django.db.models import ExpressionWrapper
from django.db.models import IntegerField
from django.db.models import Q
from django.db.models import Value
from django.db.models.fields import BooleanField
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import BooleanFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from adhocracy4.api.permissions import ViewSetRulesPermission
from adhocracy4.comments.models import Comment
from adhocracy4.filters.rest_filters import DefaultsRestFilterSet
from adhocracy4.filters.rest_filters import DistinctOrderingFilter
from adhocracy4.projects.models import Project
from apps.ideas.models import Idea
from apps.mapideas.models import MapIdea
from apps.projects import helpers

from . import serializers


class ModerationCommentFilterSet(DefaultsRestFilterSet):
    is_reviewed = BooleanFilter()
    has_reports = BooleanFilter()

    defaults = {"is_reviewed": "false", "has_reports": "all"}


class ModerationCommentPagination(PageNumberPagination):
    page_size_query_param = "num_of_comments"
    max_page_size = 1000


class ModerationCommentViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.ModerationCommentSerializer
    pagination_class = ModerationCommentPagination
    permission_classes = (ViewSetRulesPermission,)
    filter_backends = (DjangoFilterBackend, DistinctOrderingFilter)
    filterset_class = ModerationCommentFilterSet
    ordering_fields = ["created", "num_reports"]
    ordering = ["-num_reports"]
    # sets the attr for the distinct ordering in DistinctOrderingFilter
    distinct_ordering = "-created"
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
        num_reports = Count("reports", distinct=True)
        return all_comments_project.annotate(num_reports=num_reports).annotate(
            has_reports=ExpressionWrapper(
                Q(num_reports__gt=0), output_field=BooleanField()
            )
        )

    def update(self, request, *args, **kwargs):
        # if "is_blocked" in self.request.data and request.data["is_blocked"]:
        # NotifyCreatorOnModeratorBlocked.send(self.get_object())
        return super().update(request, *args, **kwargs)

    @action(detail=True)
    def mark_read(self, request, **kwargs):
        comment = self.get_object()
        comment.is_reviewed = True
        comment.save(ignore_modified=True)
        serializer = self.get_serializer(comment)

        return Response(data=serializer.data, status=200)

    @action(detail=True)
    def mark_unread(self, request, **kwargs):
        comment = self.get_object()
        comment.is_reviewed = False
        comment.save(ignore_modified=True)
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


class ModerationItemPermission(ViewSetRulesPermission):
    def get_model_cls(self, request, view):
        return Comment


class ModerationItemViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Combined list of comments and ideas for a project's moderation dashboard."""

    serializer_class = serializers.ModerationItemSerializer
    pagination_class = ModerationCommentPagination
    permission_classes = (ModerationItemPermission,)

    def dispatch(self, request, *args, **kwargs):
        self.project_pk = kwargs.get("project_pk", "")
        return super().dispatch(request, *args, **kwargs)

    @property
    def project(self):
        return get_object_or_404(Project, pk=self.project_pk)

    def get_permission_object(self):
        return self.project

    def get_queryset(self):
        params = self.request.query_params
        content_type = params.get("content_type", "all")
        is_reviewed = params.get("is_reviewed", "false")
        ordering = params.get("ordering", "-num_reports")

        row_sets = []
        if content_type in ("all", "comments", "reported"):
            comments = self._comments_queryset(is_reviewed)
            if content_type == "reported":
                comments = comments.filter(num_reports__gt=0)
            row_sets.append(self._comment_rows(comments))
        if content_type in ("all", "ideas"):
            row_sets.append(
                self._idea_rows(
                    Idea.objects.filter(module__project=self.project), "idea"
                )
            )
            row_sets.append(
                self._idea_rows(
                    MapIdea.objects.filter(module__project=self.project), "mapidea"
                )
            )
        if not row_sets:
            return Comment.objects.none()
        return self._order_rows(row_sets[0].union(*row_sets[1:], all=True), ordering)

    def _comments_queryset(self, is_reviewed):
        comments = helpers.get_all_comments_project(self.project).annotate(
            num_reports=Count("reports", distinct=True)
        )
        if is_reviewed.lower() != "all":
            comments = comments.filter(is_reviewed=is_reviewed.lower() == "true")
        return comments

    @staticmethod
    def _comment_rows(comments):
        return (
            comments.annotate(item_type=Value("comment", output_field=CharField()))
            .values("pk", "created", "num_reports", "item_type")
            .order_by()
        )

    @staticmethod
    def _idea_rows(ideas, item_type):
        return (
            ideas.annotate(
                item_type=Value(item_type, output_field=CharField()),
                num_reports=Value(0, output_field=IntegerField()),
            )
            .values("pk", "created", "num_reports", "item_type")
            .order_by()
        )

    @staticmethod
    def _order_rows(rows, ordering):
        field = ordering.lstrip("-")
        if field not in ("num_reports", "created"):
            field = "created"
        prefix = "-" if ordering.startswith("-") else ""
        return rows.order_by(prefix + field, "-created")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(self._resolve_items(page), many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self._resolve_items(queryset), many=True)
        return Response(serializer.data)

    def _resolve_items(self, rows):
        rows = list(rows)
        comment_ids = [row["pk"] for row in rows if row["item_type"] == "comment"]
        idea_ids = [row["pk"] for row in rows if row["item_type"] == "idea"]
        map_idea_ids = [row["pk"] for row in rows if row["item_type"] == "mapidea"]
        related = ("creator", "module__project__organisation")

        comments = {
            comment.pk: comment
            for comment in Comment.objects.filter(pk__in=comment_ids)
            .annotate(num_reports=Count("reports", distinct=True))
            .select_related("creator")
        }
        ideas = {
            idea.pk: idea
            for idea in Idea.objects.filter(pk__in=idea_ids).select_related(*related)
        }
        map_ideas = {
            map_idea.pk: map_idea
            for map_idea in MapIdea.objects.filter(pk__in=map_idea_ids).select_related(
                *related
            )
        }

        resolved = []
        for row in rows:
            item_type = row["item_type"]
            if item_type == "comment":
                item = comments.get(row["pk"])
            elif item_type == "idea":
                item = ideas.get(row["pk"])
            else:
                item = map_ideas.get(row["pk"])
            if item is not None:
                resolved.append(item)
        return resolved

    @property
    def rules_method_map(self):
        return ViewSetRulesPermission.default_rules_method_map._replace(
            GET="a4_candy_userdashboard.view_moderation_comment",
            OPTIONS="a4_candy_userdashboard.view_moderation_comment",
        )
