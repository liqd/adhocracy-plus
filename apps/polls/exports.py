from django.utils.translation import pgettext
from django.utils.translation import ugettext as _
from rules.contrib.views import PermissionRequiredMixin

from adhocracy4.comments.models import Comment
from adhocracy4.exports import mixins
from adhocracy4.exports import views as a4_export_views


class PollCommentExportView(
        PermissionRequiredMixin,
        mixins.ItemExportWithLinkMixin,
        mixins.ExportModelFieldsMixin,
        mixins.UserGeneratedContentExportMixin,
        mixins.ItemExportWithRatesMixin,
        mixins.CommentExportWithRepliesToMixin,
        a4_export_views.BaseItemExportView
):

    model = Comment

    fields = ['id', 'comment', 'created']
    permission_required = 'a4_candy_polls.change_poll'

    def get_permission_object(self):
        return self.module

    def get_queryset(self):
        comments = (
            Comment.objects.filter(poll__module=self.module) |
            Comment.objects.filter(parent_comment__poll__module=self.module)
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
