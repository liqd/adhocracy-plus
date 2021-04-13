import pytest


@pytest.mark.django_db
def test_comment_text_does_not_change(user_classification_factory,
                                      comment_factory,
                                      idea):
    comment = comment_factory(content_object=idea)
    comment_text = comment.comment
    classification = user_classification_factory(comment=comment)
    comment.comment = 'Changed comment text'
    comment.save()
    classification.refresh_from_db()
    assert classification.comment.comment == 'Changed comment text'
    assert classification.comment_text == comment_text
