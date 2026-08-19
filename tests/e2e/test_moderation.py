import pytest
from django.urls import reverse
from playwright.sync_api import expect

from adhocracy4.comments import models as comment_models
from adhocracy4.polls.phases import VotingPhase
from apps.moderatorfeedback.models import ModeratorCommentFeedback
from tests.factories import CommentFactory
from tests.factories import ReportFactory
from tests.factories import UserFactory
from tests.ideas.factories import IdeaFactory


@pytest.fixture
def moderation_data(e2e_active_phase, seed):
    """Project with a reported comment that the moderator can review."""
    data = e2e_active_phase(VotingPhase())
    project = data["project"]

    idea = seed(IdeaFactory, module=data["module"])
    commenter = seed(UserFactory)
    comment = seed(
        CommentFactory,
        content_object=idea,
        comment="Reported moderation comment",
        creator=commenter,
    )
    reporter = seed(UserFactory)
    seed(ReportFactory, content_object=comment, creator=reporter)

    moderator = seed(UserFactory)

    def _add_moderator():
        project.moderators.add(moderator)
        return moderator

    seed(_add_moderator)

    return {**data, "comment": comment, "moderator": moderator}


def _get_detail_url(project):
    return reverse("userdashboard-moderation-detail", kwargs={"slug": project.slug})


def _open_moderation_detail(page, e2e_login, moderation_data):
    e2e_login(moderation_data["moderator"])
    page.goto(reverse("userdashboard-moderation"))

    tile = page.locator(f'a[href="{_get_detail_url(moderation_data["project"])}"]')
    expect(tile).to_be_visible()
    tile.click()


def _notification(page, comment):
    notification = page.locator("li").filter(has_text=comment.comment)
    expect(notification).to_be_visible()
    return notification


@pytest.mark.e2e
def test_moderator_marks_reported_comment_as_read(
    page, e2e_login, moderation_data, db_commit
):
    comment = moderation_data["comment"]

    _open_moderation_detail(page, e2e_login, moderation_data)

    notification = _notification(page, comment)
    notification.locator("button.dropdown-toggle").click()
    page.get_by_role("button", name="Mark as read").click()

    expect(notification).not_to_be_attached(timeout=15000)

    def _verify():
        return comment_models.Comment.objects.get(pk=comment.pk).is_reviewed

    assert db_commit(_verify) is True


@pytest.mark.e2e
def test_moderator_blocks_comment(page, e2e_login, moderation_data, db_commit):
    comment = moderation_data["comment"]

    _open_moderation_detail(page, e2e_login, moderation_data)

    notification = _notification(page, comment)
    block = notification.locator(
        f"[id='moderation-notification-actions-bar-button-block-{comment.pk}']"
    )
    block.click()
    expect(page.locator("#alert")).to_contain_text("Comment blocked successfully.")

    def _verify():
        return comment_models.Comment.objects.get(pk=comment.pk).is_blocked

    assert db_commit(_verify) is True


@pytest.mark.e2e
def test_moderator_highlights_comment(page, e2e_login, moderation_data, db_commit):
    comment = moderation_data["comment"]

    _open_moderation_detail(page, e2e_login, moderation_data)

    notification = _notification(page, comment)
    highlight = notification.locator(
        f"[id='moderation-notification-actions-bar-button-highlight-{comment.pk}']"
    )
    highlight.click()
    expect(page.locator("#alert")).to_contain_text("Comment highlighted successfully.")

    def _verify():
        return comment_models.Comment.objects.get(pk=comment.pk).is_moderator_marked

    assert db_commit(_verify) is True


@pytest.mark.e2e
def test_moderator_adds_and_deletes_feedback(
    page, e2e_login, moderation_data, db_commit
):
    comment = moderation_data["comment"]

    _open_moderation_detail(page, e2e_login, moderation_data)

    notification = _notification(page, comment)
    notification.locator("[id*='-reply-']").click()

    feedback_form = page.locator("form.general-form")
    expect(feedback_form).to_be_visible()
    feedback_form.locator("textarea").fill("Please clarify this comment")
    feedback_form.get_by_role("button", name="submit feedback").click()

    feedback = page.locator(".userdashboard-mod-feedback")
    expect(feedback).to_be_visible()
    expect(feedback).to_contain_text("Please clarify this comment")

    def _verify():
        return ModeratorCommentFeedback.objects.filter(comment=comment).exists()

    assert db_commit(_verify) is True

    feedback.locator(".dropdown-toggle").click()
    page.locator("#delete-input").click()

    expect(feedback).not_to_be_attached(timeout=15000)

    def _verify_deleted():
        return not ModeratorCommentFeedback.objects.filter(comment=comment).exists()

    assert db_commit(_verify_deleted) is True
