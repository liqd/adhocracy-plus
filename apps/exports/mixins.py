from django.conf import settings
from django.utils.translation import gettext as _

from adhocracy4.exports.mixins import VirtualFieldMixin


class CommentExportWithCategoriesMixin(VirtualFieldMixin):
    """
    Adds categories to the comment export.

    To be used with comments with categories like in the debate module.

    ATTENTION: if this export is used elsewhere, do not copy over,
    but move to A4 (as the comments are also there!)
    """

    def get_virtual_fields(self, virtual):
        if "categories" not in virtual:
            virtual["categories"] = _("Categories")
        return super().get_virtual_fields(virtual)

    def get_categories_data(self, item):
        category_choices = getattr(settings, "A4_COMMENT_CATEGORIES", "")
        if category_choices:
            category_choices = dict((x, str(y)) for x, y in category_choices)
        if hasattr(item, "comment_categories") and item.comment_categories:
            categories = []
            category_list = item.comment_categories.strip("[]").split(",")
            for category in category_list:
                if category in category_choices:
                    categories.append(category_choices[category])
                else:
                    categories.append(category)
            return ", ".join(categories)
        return ""
