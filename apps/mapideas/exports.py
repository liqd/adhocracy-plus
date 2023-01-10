from django.utils.translation import gettext as _
from django.utils.translation import pgettext
from rules.contrib.views import PermissionRequiredMixin

from adhocracy4.comments.models import Comment
from adhocracy4.exports import mixins
from adhocracy4.exports import views as a4_export_views

from . import models


class MapIdeaExportView(
    PermissionRequiredMixin,
    mixins.ItemExportWithReferenceNumberMixin,
    mixins.ItemExportWithLinkMixin,
    mixins.ExportModelFieldsMixin,
    mixins.ItemExportWithCategoriesMixin,
    mixins.ItemExportWithLabelsMixin,
    mixins.ItemExportWithLocationMixin,
    mixins.UserGeneratedContentExportMixin,
    mixins.ItemExportWithRatesMixin,
    mixins.ItemExportWithCommentCountMixin,
    mixins.ItemExportWithModeratorFeedback,
    mixins.ItemExportWithModeratorRemark,
    a4_export_views.BaseItemExportView,
):
    model = models.MapIdea
    fields = ["name", "description"]
    html_fields = ["description"]
    permission_required = "a4_candy_mapideas.moderate_mapidea"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(module=self.module)
            .annotate_comment_count()
            .annotate_positive_rating_count()
            .annotate_negative_rating_count()
        )

    def get_permission_object(self):
        return self.module

    @property
    def raise_exception(self):
        return self.request.user.is_authenticated


class MapIdeaCommentExportView(
    PermissionRequiredMixin,
    mixins.ItemExportWithLinkMixin,
    mixins.ExportModelFieldsMixin,
    mixins.UserGeneratedContentExportMixin,
    mixins.ItemExportWithRatesMixin,
    mixins.CommentExportWithRepliesToReferenceMixin,
    mixins.CommentExportWithRepliesToMixin,
    a4_export_views.BaseItemExportView,
):

    model = Comment

    fields = ["id", "comment", "created"]
    permission_required = "a4_candy_mapideas.moderate_mapidea"

    def get_queryset(self):
        comments = Comment.objects.filter(
            mapidea__module=self.module
        ) | Comment.objects.filter(parent_comment__mapidea__module=self.module)

        return comments

    def get_permission_object(self):
        return self.module

    def get_virtual_fields(self, virtual):
        virtual.setdefault("id", _("ID"))
        virtual.setdefault("comment", pgettext("noun", "Comment"))
        virtual.setdefault("created", _("Created"))
        return super().get_virtual_fields(virtual)

    @property
    def raise_exception(self):
        return self.request.user.is_authenticated
