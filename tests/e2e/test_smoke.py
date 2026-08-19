import pytest
from django.urls import reverse
from playwright.sync_api import expect

from tests.factories import UserFactory


@pytest.mark.e2e
def test_landing_page_renders(page):
    page.goto("/")
    body = page.locator("body")
    expect(body).to_be_visible()
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


@pytest.mark.e2e
def test_guest_login_flow(page, db_commit):
    page.goto(reverse("guest_create"))

    def _guest_counts():
        from guest_user.models import Guest

        return Guest.objects.count()

    count_before = db_commit(_guest_counts)

    page.locator('input[name="terms_of_use"]').check()
    page.get_by_role("button", name="Continue as a guest").click()

    page.wait_for_url("/")

    assert db_commit(_guest_counts) == count_before + 1

    header = page.locator("header").inner_text()
    assert "Log in" not in header
