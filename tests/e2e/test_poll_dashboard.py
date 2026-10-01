import pytest
from django.urls import reverse
from playwright.sync_api import expect

from adhocracy4.polls import models as poll_models
from adhocracy4.polls.phases import VotingPhase
from adhocracy4.test.factories.polls import ChoiceFactory
from adhocracy4.test.factories.polls import PollFactory
from adhocracy4.test.factories.polls import QuestionFactory


@pytest.fixture
def poll_dashboard_data(e2e_active_phase, seed):
    """Project with a poll, two questions and an initiator member."""
    data = e2e_active_phase(VotingPhase())
    poll = seed(PollFactory, module=data["module"])
    question_one = seed(QuestionFactory, poll=poll, label="Question one", weight=1)
    question_two = seed(QuestionFactory, poll=poll, label="Question two", weight=2)
    seed(ChoiceFactory, question=question_one, label="A")
    seed(ChoiceFactory, question=question_one, label="B")
    seed(ChoiceFactory, question=question_two, label="C")
    seed(ChoiceFactory, question=question_two, label="D")
    return {**data, "poll": poll}


def _poll_dashboard_url(module):
    return reverse(
        "a4dashboard:poll-dashboard",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )


@pytest.mark.e2e
def test_initiator_reorders_questions_by_drag_and_drop(
    page, e2e_login, poll_dashboard_data, db_commit
):
    module = poll_dashboard_data["module"]
    initiator = module.project.organisation.initiators.first()

    e2e_login(initiator)
    page.goto(_poll_dashboard_url(module))

    items = page.locator(".poll-management__item")
    expect(items).to_have_count(2)
    expect(items.nth(0)).to_contain_text("Question one")
    expect(items.nth(1)).to_contain_text("Question two")

    items.nth(0).drag_to(items.nth(1))
    expect(items.nth(0)).to_contain_text("Question two")
    expect(items.nth(1)).to_contain_text("Question one")

    page.get_by_role("button", name="Save", exact=True).click()
    expect(page.locator("#alert")).to_contain_text("The poll has been updated.")

    def _verify():
        return list(
            poll_models.Question.objects.filter(poll=poll_dashboard_data["poll"])
            .order_by("weight")
            .values_list("label", flat=True)
        )

    assert db_commit(_verify) == ["Question two", "Question one"]


@pytest.mark.e2e
def test_initiator_expands_and_collapses_questions(
    page, e2e_login, poll_dashboard_data
):
    module = poll_dashboard_data["module"]
    initiator = module.project.organisation.initiators.first()

    e2e_login(initiator)
    page.goto(_poll_dashboard_url(module))

    items = page.locator(".poll-management__item")
    expect(items).to_have_count(2)

    items.nth(0).locator(".poll-management__summary").click()
    editor = page.locator(".poll-management__editor")
    expect(editor).to_have_count(1)
    expect(editor).to_contain_text("Question 1 of 2")

    # clicking the row again collapses the item, keeping the local edits
    page.locator(".poll-management__summary").first.click()
    expect(editor).to_have_count(0)

    # re-open and cancel reverts to the state from when it was opened
    items.nth(0).locator(".poll-management__summary").click()
    editor.locator("textarea").first.fill("Edited question")
    editor.get_by_role("button", name="Cancel").click()
    expect(editor).to_have_count(0)
    expect(items.nth(0)).to_contain_text("Question one")
