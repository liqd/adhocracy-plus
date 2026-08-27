import pytest
from django.urls import reverse
from django.utils import timezone
from playwright.sync_api import expect

from adhocracy4.test.factories import PhaseFactory
from apps.documents.models import Chapter
from apps.documents.phases import CommentPhase


@pytest.fixture
def text_review_module(seed):
    """Project with a Text Review (TR) module and an active comment phase."""
    now = timezone.now()
    phase = seed(
        PhaseFactory,
        phase_content=CommentPhase(),
        start_date=now - timezone.timedelta(days=1),
        end_date=now + timezone.timedelta(days=1),
    )
    module = phase.module
    module.blueprint_type = "TR"
    module.save()
    return {"module": module, "project": module.project}


def _document_dashboard_url(module):
    return reverse(
        "a4dashboard:dashboard-document-settings",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )


@pytest.mark.e2e
def test_initiator_renames_and_saves_chapter(
    page, e2e_login, text_review_module, db_commit
):
    module = text_review_module["module"]
    initiator = text_review_module["project"].organisation.initiators.first()

    e2e_login(initiator)
    page.goto(_document_dashboard_url(module))

    chapter_input = page.locator("#id_chapters-local_1-name")
    expect(chapter_input).to_be_visible()
    chapter_input.fill("Our first chapter")

    page.get_by_role("button", name="Save").click()
    expect(page.locator("#alert")).to_contain_text("The document has been updated.")

    def _verify():
        chapter = Chapter.objects.filter(module=module).order_by("id").first()
        return chapter.name if chapter else None

    assert db_commit(_verify) == "Our first chapter"
