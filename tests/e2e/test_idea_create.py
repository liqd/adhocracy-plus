import pytest
from django.urls import reverse
from django.utils import timezone

from adhocracy4.test.factories import PhaseFactory
from apps.ideas import models as idea_models
from apps.ideas import phases as idea_phases
from tests.factories import UserFactory


def _create_idea_project():
    now = timezone.now()
    phase = PhaseFactory(
        phase_content=idea_phases.IssuePhase(),
        start_date=now - timezone.timedelta(days=1),
        end_date=now + timezone.timedelta(days=1),
    )
    module = phase.module
    project = module.project
    user = UserFactory()
    return {"phase": phase, "module": module, "project": project, "user": user}


@pytest.fixture
def idea_project(seed):
    """Create a live project with an active idea-collection phase.

    Data is committed (via the seed helper) so the live server can see it.
    """
    return seed(_create_idea_project)


@pytest.mark.e2e
def test_user_creates_idea(page, e2e_login, seed, idea_project, db_commit):
    module = idea_project["module"]
    user = idea_project["user"]
    create_url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )

    e2e_login(user)

    page.goto(create_url)
    page.locator('input[name="name"]').fill("My Playwright Idea")

    # description is a CKEditor5 field: the source <textarea> is hidden and a
    # contenteditable editor is shown in its place. Interact with the editor.
    editor = page.locator(".ck-editor__editable").first
    page.wait_for_timeout(300)
    editor.click()
    editor.fill("Created by an e2e test.")

    page.locator('input[name="organisation_terms_of_use"]').check()
    page.get_by_role("button", name="Save").click()

    def _verify():
        created = idea_models.Idea.objects.get(name="My Playwright Idea")
        return created

    created = db_commit(_verify)
    assert created.creator == user
    assert created.module == module

    body = page.locator("body").inner_text()
    assert "My Playwright Idea" in body
