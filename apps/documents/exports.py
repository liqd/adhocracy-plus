from django.utils.translation import pgettext
from django.utils.translation import ugettext as _
from rules.contrib.views import PermissionRequiredMixin

from adhocracy4.comments.models import Comment
from adhocracy4.exports import mixins as a4_export_mixins
from adhocracy4.exports import views as a4_export_views
from apps.exports import mixins as export_mixins


class DocumentExportView(
        PermissionRequiredMixin,
        a4_export_mixins.ItemExportWithLinkMixin,
        a4_export_mixins.ExportModelFieldsMixin,
        export_mixins.UserGeneratedContentExportMixin,
        a4_export_mixins.ItemExportWithRatesMixin,
        export_mixins.CommentExportWithRepliesToMixin,
        a4_export_views.BaseItemExportView
):

    model = Comment
    permission_required = 'a4_candy_documents.change_chapter'

    fields = ['id', 'comment', 'created']

    def get_permission_object(self):
        return self.module

    def get_queryset(self):
        comments = (
            Comment.objects.filter(paragraph__chapter__module=self.module) |
            Comment.objects.filter(chapter__module=self.module) |
            Comment.objects.filter(
                parent_comment__paragraph__chapter__module=self.module) |
            Comment.objects.filter(parent_comment__chapter__module=self.module)
        )
        return comments

    def get_virtual_fields(self, virtual):
        virtual.setdefault('id', _('ID'))
        virtual.setdefault('comment', pgettext('noun', 'Comment'))
        virtual.setdefault('created', _('Created'))
        return super().get_virtual_fields(virtual)

    @property
    def raise_exception(self):
        return self.request.user.is_authenticated
