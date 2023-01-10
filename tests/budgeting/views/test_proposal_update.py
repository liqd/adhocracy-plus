import pytest
from django.urls import reverse

from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import freeze_post_phase
from adhocracy4.test.helpers import redirect_target
from adhocracy4.test.helpers import setup_phase
from apps.budgeting import models
from apps.budgeting import phases


@pytest.mark.django_db
def test_creator_can_update_during_active_phase(
    client, phase_factory, proposal_factory, category_factory, area_settings_factory
):
    phase, module, project, proposal = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    area_settings_factory(module=module)
    category = category_factory(module=module)
    user = proposal.creator
    url = reverse(
        "a4_candy_budgeting:proposal-update",
        kwargs={
            "organisation_slug": proposal.project.organisation.slug,
            "pk": proposal.pk,
            "year": proposal.created.year,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        data = {
            "name": "Another Proposal",
            "description": "changed description",
            "category": category.pk,
            "budget": 123,
            "point": (0, 0),
            "point_label": "somewhere",
            "organisation_terms_of_use": True,
        }
        response = client.post(url, data)
        assert redirect_target(response) == "proposal-detail"
        assert response.status_code == 302
        updated_proposal = models.Proposal.objects.get(id=proposal.pk)
        assert updated_proposal.description == "changed description"


@pytest.mark.django_db
def test_creator_cannot_update_past_phase(
    client, phase_factory, proposal_factory, category_factory
):
    phase, module, project, proposal = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    category = category_factory(module=module)
    user = proposal.creator
    assert user not in project.moderators.all()
    url = reverse(
        "a4_candy_budgeting:proposal-update",
        kwargs={
            "organisation_slug": proposal.project.organisation.slug,
            "pk": proposal.pk,
            "year": proposal.created.year,
        },
    )
    with freeze_post_phase(phase):
        client.login(username=user.email, password="password")
        data = {
            "name": "Another Proposal",
            "description": "changed description",
            "category": category.pk,
            "budget": 123,
            "organisation_terms_of_use": True,
        }
        response = client.post(url, data)
        assert response.status_code == 403


@pytest.mark.django_db
def test_moderator_can_update_past_phase(
    client, phase_factory, proposal_factory, category_factory, area_settings_factory
):
    phase, module, project, proposal = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    area_settings_factory(module=module)
    category = category_factory(module=module)
    user = proposal.creator
    moderator = project.moderators.first()
    assert moderator is not user
    url = reverse(
        "a4_candy_budgeting:proposal-update",
        kwargs={
            "organisation_slug": proposal.project.organisation.slug,
            "pk": proposal.pk,
            "year": proposal.created.year,
        },
    )
    with freeze_post_phase(phase):
        client.login(username=moderator.email, password="password")
        data = {
            "name": "Another Proposal",
            "description": "changed description",
            "category": category.pk,
            "budget": 123,
            "point": (0, 0),
            "point_label": "somewhere else",
            "organisation_terms_of_use": True,
        }
        response = client.post(url, data)
        assert redirect_target(response) == "proposal-detail"
        assert response.status_code == 302
        updated_proposal = models.Proposal.objects.get(id=proposal.pk)
        assert updated_proposal.description == "changed description"


@pytest.mark.django_db
def test_creator_cannot_update(client, proposal_factory):
    proposal = proposal_factory()
    user = proposal.creator
    assert user not in proposal.module.project.moderators.all()
    url = reverse(
        "a4_candy_budgeting:proposal-update",
        kwargs={
            "organisation_slug": proposal.project.organisation.slug,
            "pk": proposal.pk,
            "year": proposal.created.year,
        },
    )
    client.login(username=user.email, password="password")
    data = {
        "name": "Another Proposal",
        "description": "changed description",
        "budget": 123,
        "organisation_terms_of_use": True,
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderators_can_always_update(
    client, phase_factory, proposal_factory, category_factory, area_settings_factory
):
    phase, module, project, proposal = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    area_settings_factory(module=module)
    category = category_factory(module=module)
    user = proposal.creator
    moderator = project.moderators.first()
    assert moderator is not user
    url = reverse(
        "a4_candy_budgeting:proposal-update",
        kwargs={
            "organisation_slug": proposal.project.organisation.slug,
            "pk": proposal.pk,
            "year": proposal.created.year,
        },
    )
    client.login(username=moderator.email, password="password")
    data = {
        "name": "Another Proposal",
        "description": "changed description",
        "category": category.pk,
        "budget": 123,
        "point": (0, 0),
        "point_label": "somewhere",
        "organisation_terms_of_use": True,
    }
    response = client.post(url, data)
    assert redirect_target(response) == "proposal-detail"
    assert response.status_code == 302
    updated_proposal = models.Proposal.objects.get(id=proposal.pk)
    assert updated_proposal.description == "changed description"


@pytest.mark.django_db
def test_moderators_can_update_only_with_terms_agreement(
    client, proposal_factory, organisation_terms_of_use_factory, area_settings_factory
):
    proposal = proposal_factory()
    area_settings_factory(module=proposal.module)
    moderator = proposal.module.project.moderators.first()
    assert moderator is not proposal.creator
    url = reverse(
        "a4_candy_budgeting:proposal-update",
        kwargs={
            "organisation_slug": proposal.project.organisation.slug,
            "pk": proposal.pk,
            "year": proposal.created.year,
        },
    )
    client.login(username=moderator.email, password="password")
    data = {
        "name": "Another mappy Idea",
        "description": "changed description",
        "budget": 123,
        "point": (0, 0),
    }
    response = client.post(url, data)
    assert response.status_code == 200

    organisation_terms_of_use_factory(
        user=moderator,
        organisation=proposal.module.project.organisation,
        has_agreed=True,
    )
    response = client.post(url, data)
    assert redirect_target(response) == "proposal-detail"
    assert response.status_code == 302
    updated_idea = models.Proposal.objects.get(id=proposal.pk)
    assert updated_idea.description == "changed description"
