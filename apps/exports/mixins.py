from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from adhocracy4.exports import unescape_and_strip_html
from adhocracy4.exports.mixins import VirtualFieldMixin


class ItemExportWithReferenceNumberMixin(VirtualFieldMixin):

    def get_virtual_fields(self, virtual):
        if 'reference_number' not in virtual:
            virtual['reference_number'] = _('Reference No.')
        return super().get_virtual_fields(virtual)

    def get_reference_number_data(self, item):
        if hasattr(item, 'reference_number'):
            return item.reference_number
        return ''


class ItemExportWithModeratorFeedback(VirtualFieldMixin):
    def get_virtual_fields(self, virtual):
        if 'moderator_feedback' not in virtual:
            virtual['moderator_feedback'] = _('Moderator feedback')
        if 'moderator_statement' not in virtual:
            virtual['moderator_statement'] = _('Official Statement')
        return super().get_virtual_fields(virtual)

    def get_moderator_feedback_data(self, item):
        return item.get_moderator_feedback_display()

    def get_moderator_statement_data(self, item):
        if item.moderator_statement:
            return unescape_and_strip_html(item.moderator_statement.statement)
        return ''


class ItemExportWithModeratorRemark(VirtualFieldMixin):
    def get_virtual_fields(self, virtual):
        if 'moderator_remark' not in virtual:
            virtual['moderator_remark'] = _('Remark')
        return super().get_virtual_fields(virtual)

    def get_moderator_remark_data(self, item):
        remark = item.remark
        if remark:
            return unescape_and_strip_html(remark.remark)
        return ''


class UserGeneratedContentExportMixin(VirtualFieldMixin):
    def get_virtual_fields(self, virtual):
        if 'creator' not in virtual:
            virtual['creator'] = _('Creator')
        if 'created' not in virtual:
            virtual['created'] = _('Created')
        return super().get_virtual_fields(virtual)

    def get_creator_data(self, item):
        return item.creator.username

    def get_created_data(self, item):
        return item.created.isoformat()


class CommentExportWithRepliesToMixin(VirtualFieldMixin):
    def get_virtual_fields(self, virtual):
        virtual['replies_to'] = _('Reply to Comment')
        return super().get_virtual_fields(virtual)

    def get_replies_to_data(self, comment):
        try:
            return comment.parent_comment.get().pk
        except ObjectDoesNotExist:
            return ''


class CommentExportWithCategoriesMixin(VirtualFieldMixin):

    def get_virtual_fields(self, virtual):
        if 'categories' not in virtual:
            virtual['categories'] = _('Categories')
        return super().get_virtual_fields(virtual)

    def get_categories_data(self, item):
        category_choices = getattr(settings,
                                   'A4_COMMENT_CATEGORIES', '')
        if category_choices:
            category_choices = dict((x, str(y)) for x, y
                                    in category_choices)
        if hasattr(item, 'comment_categories') and item.comment_categories:
            categories = []
            category_list = item.comment_categories.strip('[]').split(',')
            for category in category_list:
                if category in category_choices:
                    categories.append(category_choices[category])
                else:
                    categories.append(category)
            return ", ".join(categories)
        return ''


class ReferenceExportWithRepliesToMixin(VirtualFieldMixin):
    def get_virtual_fields(self, virtual):
        virtual['replies_to_reference'] = _('Reply to Reference')
        return super().get_virtual_fields(virtual)

    def get_replies_to_reference_data(self, comment):
        if hasattr(comment.content_object, 'reference_number'):
            return comment.content_object.reference_number
        else:
            return ''
