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


@pytest.mark.django_db
def test_creator_can_update_creator_contact_fields_on_proposal(
    client, phase_factory, proposal_factory, area_settings_factory
):
    """Test that user can update creator contact fields when editing a proposal."""
    phase, module, project, proposal = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    area_settings_factory(module=module)

    # Get the actual creator of the proposal
    user = proposal.creator

    # Set initial values
    proposal.creator_email = "initial@example.com"
    proposal.creator_phone = "+1111111111"
    proposal.creator_contact_consent = False
    proposal.save()

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

        update_data = {
            "name": proposal.name,
            "description": proposal.description,
            "budget": 123,
            "point": (0, 0),
            "point_label": "somewhere",
            "organisation_terms_of_use": True,
            "creator_email": "updated@example.com",
            "creator_phone": "+9876543210",
            "creator_contact_consent": True,
        }

        if proposal.category:
            update_data["category"] = proposal.category.pk

        response = client.post(url, update_data)
        assert response.status_code == 302
        assert redirect_target(response) == "proposal-detail"

        proposal.refresh_from_db()
        assert proposal.creator_email == "updated@example.com"
        assert proposal.creator_phone == "+9876543210"
        assert proposal.creator_contact_consent is True


@pytest.mark.django_db
def test_proposal_contact_fields_persist_when_updating_other_fields(
    client, phase_factory, proposal_factory, area_settings_factory
):
    """Test that contact fields retain values when only other fields are updated."""
    phase, module, project, proposal = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    area_settings_factory(module=module)

    # Set initial contact values
    original_email = "persist@example.com"
    original_phone = "+9999999999"
    original_consent = True

    proposal.creator_email = original_email
    proposal.creator_phone = original_phone
    proposal.creator_contact_consent = original_consent
    proposal.save()

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

        # Update ONLY name and description - do NOT include contact fields
        update_data = {
            "name": "Brand New Proposal Name",
            "description": "This is a completely updated description",
            "budget": 123,
            "point": (0, 0),
            "point_label": "somewhere",
            "organisation_terms_of_use": True,
        }

        if proposal.category:
            update_data["category"] = proposal.category.pk

        response = client.post(url, update_data)

        assert response.status_code == 302
        assert redirect_target(response) == "proposal-detail"

        proposal.refresh_from_db()

        # Contact fields should remain unchanged
        assert proposal.creator_email == original_email
        assert proposal.creator_phone == original_phone
        assert proposal.creator_contact_consent == original_consent

        # Other fields should be updated
        assert proposal.name == "Brand New Proposal Name"
        assert proposal.description == "This is a completely updated description"


@pytest.mark.django_db
def test_proposal_contact_fields_cleared_when_consent_removed_on_update(
    client, phase_factory, proposal_factory, area_settings_factory
):
    """Test that when user unchecks consent during update, email and phone are cleared."""
    phase, module, project, proposal = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    area_settings_factory(module=module)

    # Set initial contact values WITH consent
    proposal.creator_email = "existing@example.com"
    proposal.creator_phone = "+49123456789"
    proposal.creator_contact_consent = True
    proposal.save()

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

        # Update: uncheck consent
        update_data = {
            "name": proposal.name,
            "description": proposal.description,
            "budget": 123,
            "point": (0, 0),
            "point_label": "somewhere",
            "creator_email": "shouldbeignored@example.com",
            "creator_phone": "+9999999999",
            "creator_contact_consent": False,
            "organisation_terms_of_use": True,
        }

        if proposal.category:
            update_data["category"] = proposal.category.pk

        response = client.post(url, update_data)
        assert response.status_code == 302
        assert redirect_target(response) == "proposal-detail"

        proposal.refresh_from_db()

        # Email and phone should be cleared because consent is False
        assert proposal.creator_email == ""
        assert proposal.creator_phone == ""
        assert proposal.creator_contact_consent is False


@pytest.mark.django_db
def test_proposal_contact_fields_prepopulated_in_update_form(
    client, phase_factory, proposal_factory, area_settings_factory
):
    """Test that Proposal (inheriting from AbstractIdeaUpdateView) gets contact fields pre-populated."""
    phase, module, project, proposal = setup_phase(
        phase_factory, proposal_factory, phases.RequestPhase
    )
    area_settings_factory(module=module)

    # Set initial contact values
    proposal.creator_email = "proposal_prepop@example.com"
    proposal.creator_phone = "+4987654321"
    proposal.creator_contact_consent = True
    proposal.save()

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
        response = client.get(url)

        assert response.status_code == 200
        form = response.context["form"]

        # Verify inheritance works - Proposal gets pre-populated values
        assert form.initial.get("creator_email") == "proposal_prepop@example.com"
        assert form.initial.get("creator_phone") == "+4987654321"
        assert form.initial.get("creator_contact_consent") is True
