import pytest

from adhocracy4.comments.models import Comment
from adhocracy4.exports import mixins
from apps.exports.mixins import CommentExportWithCategoriesMixin


@pytest.mark.django_db
def test_reply_to_mixin(idea, comment_factory):
    mixin = mixins.CommentExportWithRepliesToMixin()

    virtual = mixin.get_virtual_fields({})
    assert "replies_to_comment" in virtual

    comment = comment_factory(content_object=idea)
    reply_comment = comment_factory(content_object=comment)

    assert Comment.objects.count() == 2

    assert mixin.get_replies_to_comment_data(comment) == ""
    assert mixin.get_replies_to_comment_data(reply_comment) == comment.id


@pytest.mark.django_db
def test_reply_to_reference_mixin(idea, comment_factory):
    mixin = mixins.CommentExportWithRepliesToReferenceMixin()

    virtual = mixin.get_virtual_fields({})
    assert "replies_to_reference" in virtual

    comment = comment_factory(content_object=idea)
    reply_comment = comment_factory(content_object=comment)

    assert Comment.objects.count() == 2

    assert mixin.get_replies_to_reference_data(comment) == idea.reference_number
    assert mixin.get_replies_to_reference_data(reply_comment) == ""


@pytest.mark.django_db
def test_comment_export_with_categories_mixin(idea, comment_factory):
    mixin = CommentExportWithCategoriesMixin()

    virtual = mixin.get_virtual_fields({})
    assert "categories" in virtual

    comment = comment_factory(content_object=idea, comment_categories="sug")
    comment2 = comment_factory(content_object=idea, comment_categories="sug,not")
    reply_comment = comment_factory(content_object=comment)

    assert Comment.objects.count() == 3

    assert mixin.get_categories_data(comment) == "suggestion"
    assert "suggestion" in mixin.get_categories_data(comment2)
    assert "note" in mixin.get_categories_data(comment2)
    assert mixin.get_categories_data(reply_comment) == ""
