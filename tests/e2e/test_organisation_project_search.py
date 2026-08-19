import pytest
from django.urls import reverse
from django.utils import timezone
from playwright.sync_api import expect

from adhocracy4.polls.phases import VotingPhase
from adhocracy4.test.factories import ModuleFactory
from adhocracy4.test.factories import PhaseFactory
from adhocracy4.test.factories import ProjectFactory
from tests.factories import OrganisationFactory


@pytest.fixture
def org_search_data(seed):
    """Organisation with two active projects with distinct names."""
    organisation = seed(OrganisationFactory)
    alpha = seed(
        ProjectFactory,
        organisation=organisation,
        name="Alpha neighbourhood walk",
    )
    beta = seed(
        ProjectFactory,
        organisation=organisation,
        name="Beta bike lane plan",
    )

    now = timezone.now()
    for project in (alpha, beta):
        module = seed(ModuleFactory, project=project)
        seed(
            PhaseFactory,
            module=module,
            phase_content=VotingPhase(),
            start_date=now - timezone.timedelta(days=1),
            end_date=now + timezone.timedelta(days=1),
        )

    return {"organisation": organisation, "alpha": alpha, "beta": beta}


@pytest.mark.e2e
def test_organisation_project_search_filters_tiles(page, org_search_data):
    page.goto(
        reverse(
            "organisation",
            kwargs={"organisation_slug": org_search_data["organisation"].slug},
        )
    )

    search = page.locator("[data-project-search]")
    expect(search).to_be_visible()
    input = search.locator("[data-project-search-input]")

    alpha_tile = page.locator("[data-project-search-list] .tile").filter(
        has_text="Alpha neighbourhood walk"
    )
    beta_tile = page.locator("[data-project-search-list] .tile").filter(
        has_text="Beta bike lane plan"
    )
    empty = page.locator("[data-project-search-empty]")

    expect(alpha_tile).to_be_visible()
    expect(beta_tile).to_be_visible()
    expect(empty).to_be_hidden()

    input.fill("alpha")
    expect(alpha_tile).to_be_visible()
    expect(beta_tile).to_be_hidden()
    expect(empty).to_be_hidden()

    input.fill("no match anywhere")
    expect(alpha_tile).to_be_hidden()
    expect(beta_tile).to_be_hidden()
    expect(empty).to_be_visible()

    input.fill("")
    expect(alpha_tile).to_be_visible()
    expect(beta_tile).to_be_visible()
