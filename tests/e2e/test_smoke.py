import pytest

from tests.factories import UserFactory


@pytest.mark.e2e
def test_landing_page_renders(page):
    page.goto("/")
    body = page.locator("body")
    body.wait_for(state="visible")
    text = body.inner_text()
    assert "Poll" in text
    assert "Brainstorming" in text


@pytest.mark.e2e
def test_login_flow(page, e2e_login, seed):
    user = seed(UserFactory)

    e2e_login(user)
    page.wait_for_url("/")

    header = page.locator("header").inner_text()
    assert user.username in header
    assert "Log in" not in header
