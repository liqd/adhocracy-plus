import pytest
from django.db.models import signals

from adhocracy4.comments.models import Comment
from apps.classifications.signals import get_ai_classification


@pytest.mark.django_db
def test_ai_classification_receives_post_save_comment_signal(idea,
                                                             comment_factory,
                                                             caplog):
    assert(get_ai_classification in signals.post_save._live_receivers(Comment))
    comment_factory(content_object=idea,
                    comment='lala')
    assert('No ai api auth token provided.' in str(caplog.records[-1]))
