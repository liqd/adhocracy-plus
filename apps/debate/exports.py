from django.utils.translation import gettext as _
from django.utils.translation import pgettext
from rules.contrib.views import PermissionRequiredMixin

from adhocracy4.comments.models import Comment
from adhocracy4.exports import mixins
from adhocracy4.exports import views as a4_export_views
from apps.exports import mixins as export_mixins

from . import models


class SubjectExportView(
    PermissionRequiredMixin,
    mixins.ItemExportWithReferenceNumberMixin,
    mixins.ItemExportWithLinkMixin,
    mixins.ExportModelFieldsMixin,
    mixins.UserGeneratedContentExportMixin,
    mixins.ItemExportWithCommentCountMixin,
    a4_export_views.BaseItemExportView,
):
    model = models.Subject
    fields = ["name"]
    permission_required = "a4_candy_debate.change_subject"

    def get_permission_object(self):
        return self.module

    def get_queryset(self):
        return (
            super().get_queryset().filter(module=self.module).annotate_comment_count()
        )

    @property
    def raise_exception(self):
        return self.request.user.is_authenticated


class SubjectCommentExportView(
    PermissionRequiredMixin,
    mixins.ItemExportWithLinkMixin,
    mixins.ExportModelFieldsMixin,
    export_mixins.CommentExportWithCategoriesMixin,
    mixins.UserGeneratedContentExportMixin,
    mixins.ItemExportWithRatesMixin,
    mixins.CommentExportWithRepliesToReferenceMixin,
    mixins.CommentExportWithRepliesToMixin,
    a4_export_views.BaseItemExportView,
):

    model = Comment

    fields = ["id", "comment", "created"]
    permission_required = "a4_candy_debate.change_subject"

    def get_permission_object(self):
        return self.module

    def get_queryset(self):
        comments = Comment.objects.filter(
            subject__module=self.module
        ) | Comment.objects.filter(parent_comment__subject__module=self.module)

        return comments

    def get_virtual_fields(self, virtual):
        virtual.setdefault("id", _("ID"))
        virtual.setdefault("comment", pgettext("noun", "Comment"))
        virtual.setdefault("created", _("Created"))
        return super().get_virtual_fields(virtual)

    @property
    def raise_exception(self):
        return self.request.user.is_authenticated
