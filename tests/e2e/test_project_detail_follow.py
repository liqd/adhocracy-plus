import pytest
from playwright.sync_api import expect

from adhocracy4.follows import models as follow_models
from adhocracy4.polls.phases import VotingPhase
from tests.factories import UserFactory


@pytest.fixture
def follow_data(e2e_active_phase, seed):
    """A project an authenticated user can follow from the detail page."""
    data = e2e_active_phase(VotingPhase())

    def _clear_follows():
        follow_models.Follow.objects.filter(project=data["project"]).delete()
        return data["project"]

    seed(_clear_follows)
    user = seed(UserFactory)
    return {**data, "user": user}


def _follow_button(page):
    return page.locator("#project-detail-follow-actions button")


def _follow_button_text(page):
    return _follow_button(page).locator(".a4-follow__btn--content")


def _follower_label(page):
    return page.locator("#project-detail-followers-label")


@pytest.mark.e2e
def test_user_follows_and_unfollows_project(page, e2e_login, follow_data, db_commit):
    project = follow_data["project"]
    user = follow_data["user"]

    e2e_login(user)
    page.goto(project.get_absolute_url())

    button = _follow_button(page)
    expect(button).to_be_visible()
    expect(_follow_button_text(page)).to_have_text("Follow")
    expect(button).to_have_attribute("aria-pressed", "false")

    button.click()

    expect(_follow_button_text(page)).to_have_text("Following")
    expect(button).to_have_attribute("aria-pressed", "true")
    expect(_follower_label(page)).to_have_text("1 Following")
    expect(
        page.locator("#project-detail-followers-avatars .project-detail__avatar--more")
    ).to_have_count(0)

    def _followed():
        return follow_models.Follow.objects.filter(
            project=project, creator=user
        ).exists()

    assert db_commit(_followed) is True

    button.click()

    expect(_follow_button_text(page)).to_have_text("Follow")
    expect(button).to_have_attribute("aria-pressed", "false")
    expect(_follower_label(page)).to_have_text("0 Following")
    expect(
        page.locator("#project-detail-followers-avatars .project-detail__avatar--more")
    ).to_have_count(1)

    def _enabled():
        follow = follow_models.Follow.objects.filter(
            project=project, creator=user
        ).first()
        return follow.enabled if follow else False

    assert db_commit(_enabled) is False
