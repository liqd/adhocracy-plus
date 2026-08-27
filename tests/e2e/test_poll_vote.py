import pytest
from playwright.sync_api import expect

from adhocracy4.polls import models as poll_models
from adhocracy4.polls.phases import VotingPhase
from adhocracy4.test.factories.polls import ChoiceFactory
from adhocracy4.test.factories.polls import PollFactory
from adhocracy4.test.factories.polls import QuestionFactory
from tests.factories import UserFactory


@pytest.fixture
def poll_data(e2e_active_phase, seed):
    """Project with an active voting phase and a single-choice question."""
    data = e2e_active_phase(VotingPhase())
    poll = seed(PollFactory, module=data["module"], allow_unregistered_users=True)
    question = seed(
        QuestionFactory,
        poll=poll,
        label="Favorite color?",
        multiple_choice=False,
    )
    choice_a = seed(ChoiceFactory, question=question, label="Option A")
    seed(ChoiceFactory, question=question, label="Option B")
    user = seed(UserFactory)
    return {**data, "poll": poll, "choice_a": choice_a, "user": user}


@pytest.fixture
def multi_question_poll_data(e2e_active_phase, seed):
    """Project with two single-choice questions and distinct answers."""
    data = e2e_active_phase(VotingPhase())
    poll = seed(PollFactory, module=data["module"], allow_unregistered_users=True)
    question_color = seed(
        QuestionFactory,
        poll=poll,
        label="Favorite color?",
        multiple_choice=False,
        weight=1,
    )
    question_animal = seed(
        QuestionFactory,
        poll=poll,
        label="Favorite animal?",
        multiple_choice=False,
        weight=2,
    )
    choice_red = seed(ChoiceFactory, question=question_color, label="Red", weight=1)
    seed(ChoiceFactory, question=question_color, label="Blue", weight=2)
    seed(ChoiceFactory, question=question_animal, label="Dog", weight=1)
    user = seed(UserFactory)
    return {
        **data,
        "poll": poll,
        "question_color": question_color,
        "question_animal": question_animal,
        "choice_red": choice_red,
        "user": user,
    }


def _vote_flow(page):
    page.get_by_role("button", name="Start").click()
    page.get_by_text("Option A", exact=True).click()
    page.locator("#terms-of-use").check()
    page.get_by_role("button", name="Submit All").click()


def _open_poll(page, e2e_login, user, module):
    e2e_login(user)
    page.goto(module.get_absolute_url())


@pytest.mark.e2e
def test_user_votes_in_poll(page, e2e_login, poll_data, db_commit):
    module = poll_data["module"]
    choice_a = poll_data["choice_a"]

    _open_poll(page, e2e_login, poll_data["user"], module)

    _vote_flow(page)

    expect(page.locator(".poll__preliminary-results")).to_be_visible()

    def _verify():
        return poll_models.Vote.objects.filter(choice=choice_a).count()

    assert db_commit(_verify) == 1


@pytest.mark.e2e
def test_anonymous_user_votes_in_poll(page, poll_data, db_commit):
    module = poll_data["module"]

    page.goto(module.get_absolute_url())
    expect(
        page.get_by_text(
            "You can now participate in this poll even if you're not logged in."
        )
    ).to_be_visible()

    _vote_flow(page)

    expect(page.locator(".poll__preliminary-results")).to_be_visible()

    def _verify():
        return poll_models.Vote.objects.filter(choice=poll_data["choice_a"]).count()

    assert db_commit(_verify) == 1


@pytest.mark.e2e
def test_user_answers_multi_question_poll(
    page, e2e_login, multi_question_poll_data, db_commit
):
    module = multi_question_poll_data["module"]

    _open_poll(page, e2e_login, multi_question_poll_data["user"], module)

    page.get_by_role("button", name="Start").click()
    expect(page.get_by_text("Question 1 of 2", exact=True)).to_be_visible()
    expect(page.get_by_text("Favorite color?", exact=True)).to_be_visible()
    page.get_by_text("Red", exact=True).click()
    page.get_by_role("button", name="Next").click()

    expect(page.get_by_text("Question 2 of 2", exact=True)).to_be_visible()
    expect(page.get_by_text("Favorite animal?", exact=True)).to_be_visible()

    page.get_by_role("button", name="Go Back").click()
    expect(page.get_by_text("Question 1 of 2", exact=True)).to_be_visible()
    page.get_by_role("button", name="Next").click()

    expect(page.get_by_text("Question 2 of 2", exact=True)).to_be_visible()
    page.get_by_text("Dog", exact=True).click()
    page.locator("#terms-of-use").check()
    page.get_by_role("button", name="Submit All").click()

    expect(page.locator(".poll__preliminary-results")).to_be_visible()

    def _verify():
        color_votes = poll_models.Vote.objects.filter(
            choice__question=multi_question_poll_data["question_color"]
        ).count()
        animal_votes = poll_models.Vote.objects.filter(
            choice__question=multi_question_poll_data["question_animal"]
        ).count()
        return color_votes, animal_votes

    assert db_commit(_verify) == (1, 1)


@pytest.mark.e2e
def test_user_sees_and_changes_answers_on_review_step(
    page, e2e_login, multi_question_poll_data, db_commit
):
    data = multi_question_poll_data
    module = data["module"]
    poll = data["poll"]
    poll.hide_results_until_finished = True
    poll.save()

    _open_poll(page, e2e_login, data["user"], module)

    page.get_by_role("button", name="Start").click()
    page.get_by_text("Red", exact=True).click()
    page.get_by_role("button", name="Next").click()
    page.get_by_text("Dog", exact=True).click()
    page.locator("#terms-of-use").check()
    page.get_by_role("button", name="Submit All").click()

    review = page.locator(".poll-answer-review")
    expect(review).to_be_visible()
    expect(review).to_contain_text(
        "Thank you for taking part in the poll! You will see the results as soon "
        "as the participation phase is over."
    )
    expect(review.get_by_text("Favorite color?", exact=True)).to_be_visible()
    expect(review.get_by_text("Favorite animal?", exact=True)).to_be_visible()

    page.get_by_role("button", name="Change my answers").click()
    expect(page.get_by_text("Question 1 of 2", exact=True)).to_be_visible()
    page.get_by_text("Blue", exact=True).click()
    page.get_by_role("button", name="Next").click()
    expect(page.get_by_text("Question 2 of 2", exact=True)).to_be_visible()
    page.get_by_role("button", name="Submit All").click()
    expect(review).to_be_visible()

    def _verify():
        votes = poll_models.Vote.objects.filter(choice__question__poll=poll).count()
        blue_votes = poll_models.Vote.objects.filter(choice__label="Blue").count()
        red_votes = poll_models.Vote.objects.filter(choice__label="Red").count()
        return votes, blue_votes, red_votes

    assert db_commit(_verify) == (2, 1, 0)
