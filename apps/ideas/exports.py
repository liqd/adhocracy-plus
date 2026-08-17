from django.utils.translation import gettext as _
from django.utils.translation import pgettext
from rules.contrib.views import PermissionRequiredMixin

from adhocracy4.comments.models import Comment
from adhocracy4.exports import mixins
from adhocracy4.exports import views as a4_export_views

from . import models


class IdeaExportView(
    PermissionRequiredMixin,
    mixins.ItemExportWithReferenceNumberMixin,
    mixins.ItemExportWithLinkMixin,
    mixins.ItemExportWithImageMixin,
    mixins.ExportModelFieldsMixin,
    mixins.ItemExportWithCategoriesMixin,
    mixins.ItemExportWithLabelsMixin,
    mixins.UserGeneratedContentExportMixin,
    mixins.ItemExportWithRatesMixin,
    mixins.ItemExportWithCommentCountMixin,
    mixins.ItemExportWithModeratorFeedback,
    mixins.ItemExportWithModeratorRemark,
    mixins.CreatorContactExportMixin,
    a4_export_views.BaseItemExportView,
):
    model = models.Idea
    fields = ["name", "description"]
    html_fields = ["description"]
    permission_required = "a4_candy_ideas.moderate_idea"

    def get_permission_object(self):
        return self.module

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(module=self.module)
            .annotate_comment_count()
            .annotate_positive_rating_count()
            .annotate_negative_rating_count()
            .prefetch_related(
                "custom_field_answers", "custom_field_answers__field__choices"
            )
        )

    def get_virtual_fields(self, virtual):
        virtual = super().get_virtual_fields(virtual)
        settings = self.module.settings_instance
        if not (settings and hasattr(settings, "fields")):
            return virtual

        for field in settings.fields.all():
            name = "custom_field_{}".format(field.pk)
            virtual[name] = field.label
            setattr(
                self,
                "get_{}_data".format(name),
                self._make_custom_field_getter(field.pk),
            )
        return virtual

    def _make_custom_field_getter(self, field_id):
        def getter(item):
            for answer in item.custom_field_answers.all():
                if answer.field_id == field_id:
                    return answer.display_value
            return ""

        return getter

    @property
    def raise_exception(self):
        return self.request.user.is_authenticated


class IdeaCommentExportView(
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
    permission_required = "a4_candy_ideas.moderate_idea"

    def get_permission_object(self):
        return self.module

    def get_queryset(self):
        comments = Comment.objects.filter(
            idea__module=self.module
        ) | Comment.objects.filter(parent_comment__idea__module=self.module)

        return comments

    def get_virtual_fields(self, virtual):
        virtual.setdefault("id", _("ID"))
        virtual.setdefault("comment", pgettext("noun", "Comment"))
        virtual.setdefault("created", _("Created"))
        return super().get_virtual_fields(virtual)

    @property
    def raise_exception(self):
        return self.request.user.is_authenticated
