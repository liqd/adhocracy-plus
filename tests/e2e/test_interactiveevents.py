import pytest
from django.urls import reverse
from playwright.sync_api import expect

from apps.interactiveevents import models
from apps.interactiveevents import phases
from tests.factories import CategoryFactory
from tests.interactiveevents.factories import LiveQuestionFactory


@pytest.fixture
def issue_module(e2e_active_phase, seed):
    """Module with an active issue phase and one category."""
    active_phase = e2e_active_phase(phases.IssuePhase())
    module = active_phase["module"]
    category = seed(CategoryFactory, module=module)
    return {
        "module": module,
        "project": active_phase["project"],
        "category": category,
    }


def _module_url(module):
    return reverse(
        "live-question-module-detail",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )


@pytest.mark.e2e
def test_anonymous_asks_and_likes_question(page, issue_module, db_commit):
    module = issue_module["module"]
    category = issue_module["category"]

    page.goto(_module_url(module))
    page.locator("#questionTextField").fill("Does the plan reach everyone?")
    page.select_option("#categorySelect", str(category.pk))
    page.locator("#data_protection_check").check()
    page.get_by_role("button", name="Add Question").click()

    question = page.locator(".list-item", has_text="Does the plan reach everyone?")
    expect(question).to_be_visible(timeout=15000)
    like_button = question.get_by_role("button", name="add like")
    expect(like_button).to_be_visible()
    like_button.click()
    expect(question.get_by_role("button", name="undo like")).to_be_visible()

    def _verify():
        live_question = models.LiveQuestion.objects.get(
            text="Does the plan reach everyone?"
        )
        return live_question.livequestion_likes.count()

    assert db_commit(_verify) == 1


@pytest.mark.e2e
def test_filter_questions_by_category(page, issue_module, seed):
    module = issue_module["module"]
    other_category = seed(CategoryFactory, module=module)
    seed(
        LiveQuestionFactory,
        text="Visible when filtering",
        category=issue_module["category"],
        module=module,
    )
    seed(
        LiveQuestionFactory,
        text="Hidden by filter",
        category=other_category,
        module=module,
    )

    page.goto(_module_url(module))
    visible = page.locator(".list-item", has_text="Visible when filtering")
    hidden = page.locator(".list-item", has_text="Hidden by filter")
    expect(visible).to_be_visible()
    expect(hidden).to_be_visible()

    page.locator("#dropdownAffiliationBtn").click()
    page.locator(".dropdown-item", has_text=other_category.name).click()

    expect(visible).to_be_hidden()
    expect(hidden).to_be_visible()


@pytest.mark.e2e
def test_moderator_marks_question_answered(
    page, e2e_login, issue_module, seed, db_commit
):
    module = issue_module["module"]
    live_question = seed(
        LiveQuestionFactory,
        text="Please answer me",
        category=issue_module["category"],
        module=module,
    )
    e2e_login(issue_module["project"].moderators.first())

    page.goto(_module_url(module))
    question = page.locator(
        '[data-testid="question-moderator"]', has_text="Please answer me"
    )
    expect(question).to_be_visible()

    question.get_by_role("button", name="mark as done").click()

    expect(question).to_be_hidden()

    def _verify():
        return models.LiveQuestion.objects.get(pk=live_question.pk).is_answered

    assert db_commit(_verify) is True


@pytest.mark.e2e
def test_moderator_present_screen_shows_live_questions(
    page, e2e_login, issue_module, seed
):
    module = issue_module["module"]
    seed(
        LiveQuestionFactory,
        text="To present on screen",
        category=issue_module["category"],
        module=module,
        is_live=True,
    )
    seed(
        LiveQuestionFactory,
        text="Answered already",
        category=issue_module["category"],
        module=module,
        is_live=True,
        is_answered=True,
    )
    e2e_login(issue_module["project"].moderators.first())

    page.goto(
        reverse(
            "question-present",
            kwargs={
                "organisation_slug": module.project.organisation.slug,
                "module_slug": module.slug,
            },
        )
    )

    presented = page.locator(".list-item", has_text="To present on screen")
    expect(presented).to_be_visible(timeout=15000)
    answered = page.locator(".list-item", has_text="Answered already")
    expect(answered).to_be_hidden()
