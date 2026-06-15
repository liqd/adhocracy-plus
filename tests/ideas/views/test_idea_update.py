import pytest
from django.urls import reverse

from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import redirect_target
from adhocracy4.test.helpers import setup_phase
from apps.ideas import models
from apps.ideas import phases


@pytest.mark.django_db
def test_creator_can_update_during_active_phase(
    client, phase_factory, idea_factory, category_factory
):
    phase, module, project, idea = setup_phase(
        phase_factory, idea_factory, phases.IssuePhase
    )
    category = category_factory(module=module)
    user = idea.creator
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": idea.project.organisation.slug,
            "pk": idea.pk,
            "year": idea.created.year,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        data = {
            "name": "Another Idea",
            "description": "changed description",
            "category": category.pk,
            "organisation_terms_of_use": True,
        }
        response = client.post(url, data)
        assert redirect_target(response) == "idea-detail"
        assert response.status_code == 302
        updated_idea = models.Idea.objects.get(id=idea.pk)
        assert updated_idea.description == "changed description"


@pytest.mark.django_db
def test_creator_cannot_update_in_wrong_phase(
    client, phase_factory, idea_factory, category_factory
):
    phase, module, project, idea = setup_phase(
        phase_factory, idea_factory, phases.RatingPhase
    )
    category = category_factory(module=module)
    user = idea.creator
    assert user not in project.moderators.all()
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": idea.project.organisation.slug,
            "pk": idea.pk,
            "year": idea.created.year,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        data = {
            "name": "Another Idea",
            "description": "changed description",
            "category": category.pk,
            "organisation_terms_of_use": True,
        }
        response = client.post(url, data)
        assert response.status_code == 403


@pytest.mark.django_db
def test_creator_can_update_only_with_terms_agreement(
    client,
    phase_factory,
    idea_factory,
    category_factory,
    organisation_terms_of_use_factory,
):
    phase, module, project, idea = setup_phase(
        phase_factory, idea_factory, phases.IssuePhase
    )
    category = category_factory(module=module)
    user = idea.creator
    agreement = organisation_terms_of_use_factory(
        user=user,
        organisation=module.project.organisation,
        has_agreed=False,
    )
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": idea.project.organisation.slug,
            "pk": idea.pk,
            "year": idea.created.year,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        data = {
            "name": "Another Idea",
            "description": "changed description",
            "category": category.pk,
        }
        response = client.post(url, data)
        assert response.status_code == 200

        agreement.has_agreed = True
        agreement.save()
        response = client.post(url, data)
        assert redirect_target(response) == "idea-detail"
        assert response.status_code == 302
        updated_idea = models.Idea.objects.get(id=idea.pk)
        assert updated_idea.description == "changed description"


@pytest.mark.django_db
def test_moderator_can_update_during_wrong_phase(
    client, phase_factory, idea_factory, category_factory
):
    phase, module, project, idea = setup_phase(
        phase_factory, idea_factory, phases.RatingPhase
    )
    category = category_factory(module=module)
    user = idea.creator
    moderator = project.moderators.first()
    assert moderator is not user
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": idea.project.organisation.slug,
            "pk": idea.pk,
            "year": idea.created.year,
        },
    )
    with freeze_phase(phase):
        client.login(username=moderator.email, password="password")
        data = {
            "name": "Another Idea",
            "description": "changed description",
            "category": category.pk,
            "organisation_terms_of_use": True,
        }
        response = client.post(url, data)
        assert redirect_target(response) == "idea-detail"
        assert response.status_code == 302
        updated_idea = models.Idea.objects.get(id=idea.pk)
        assert updated_idea.description == "changed description"


@pytest.mark.django_db
def test_creator_cannot_update(client, idea_factory):
    idea = idea_factory()
    user = idea.creator
    assert user not in idea.module.project.moderators.all()
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": idea.project.organisation.slug,
            "pk": idea.pk,
            "year": idea.created.year,
        },
    )
    client.login(username=user.email, password="password")
    data = {
        "name": "Another Idea",
        "description": "changed description",
        "organisation_terms_of_use": True,
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderators_can_always_update(client, idea_factory):
    idea = idea_factory()
    moderator = idea.module.project.moderators.first()
    assert moderator is not idea.creator
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": idea.project.organisation.slug,
            "pk": idea.pk,
            "year": idea.created.year,
        },
    )
    client.login(username=moderator.email, password="password")
    data = {
        "name": "Another Idea",
        "description": "changed description",
        "organisation_terms_of_use": True,
    }
    response = client.post(url, data)
    assert redirect_target(response) == "idea-detail"
    assert response.status_code == 302
    updated_idea = models.Idea.objects.get(id=idea.pk)
    assert updated_idea.description == "changed description"


@pytest.mark.django_db
def test_moderators_can_update_only_with_terms_agreement(
    client, idea_factory, organisation_terms_of_use_factory
):
    idea = idea_factory()
    moderator = idea.module.project.moderators.first()
    assert moderator is not idea.creator
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": idea.project.organisation.slug,
            "pk": idea.pk,
            "year": idea.created.year,
        },
    )
    client.login(username=moderator.email, password="password")
    data = {
        "name": "Another Idea",
        "description": "changed description",
    }
    response = client.post(url, data)
    assert response.status_code == 200

    organisation_terms_of_use_factory(
        user=moderator,
        organisation=idea.module.project.organisation,
        has_agreed=True,
    )
    response = client.post(url, data)
    assert redirect_target(response) == "idea-detail"
    assert response.status_code == 302
    updated_idea = models.Idea.objects.get(id=idea.pk)
    assert updated_idea.description == "changed description"


@pytest.mark.django_db
def test_creator_contact_fields_are_prepopulated_in_update_form(
    client, phase_factory, idea_factory
):
    """Test that creator contact fields show existing values when editing an idea.

    UI bug: Fields appear empty when they should show saved values.
    """
    phase, module, project, idea = setup_phase(
        phase_factory, idea_factory, phases.IssuePhase
    )

    # Set initial contact values
    idea.creator_email = "existing@example.com"
    idea.creator_phone = "+49123456789"
    idea.creator_contact_consent = True
    idea.save()

    user = idea.creator
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "year": idea.created.year,
            "pk": idea.pk,
        },
    )

    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        response = client.get(url)

        assert response.status_code == 200

        # Access the form instance from response context
        form = response.context["form"]

        # Verify form fields are pre-populated with existing values
        assert (
            form.initial.get("creator_email") == "existing@example.com"
        ), "Email field should be pre-populated with existing value"
        assert (
            form.initial.get("creator_phone") == "+49123456789"
        ), "Phone field should be pre-populated with existing value"
        assert (
            form.initial.get("creator_contact_consent") is True
        ), "Consent checkbox should be checked when consent is True"


@pytest.mark.django_db
def test_creator_contact_fields_persist_when_updating_other_fields(
    client, phase_factory, idea_factory
):
    """Test that contact fields retain their values when only other fields are updated.

    UI bug: Contact fields reset to empty when user updates name/description only.
    """
    phase, module, project, idea = setup_phase(
        phase_factory, idea_factory, phases.IssuePhase
    )

    # Set initial contact values
    original_email = "persist@example.com"
    original_phone = "+9999999999"
    original_consent = True

    idea.creator_email = original_email
    idea.creator_phone = original_phone
    idea.creator_contact_consent = original_consent
    idea.save()

    user = idea.creator
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "year": idea.created.year,
            "pk": idea.pk,
        },
    )

    with freeze_phase(phase):
        client.login(username=user.email, password="password")

        # Update ONLY name and description - do NOT include contact fields
        update_data = {
            "name": "Brand New Idea Name",
            "description": "This is a completely updated description",
            "organisation_terms_of_use": True,
        }

        # Add category if the idea has one (required for form validation)
        if idea.category:
            update_data["category"] = idea.category.pk

        response = client.post(url, update_data)

        assert (
            response.status_code == 302
        ), f"Expected redirect (302), got {response.status_code}"
        assert redirect_target(response) == "idea-detail"

        idea.refresh_from_db()

        # Contact fields should remain unchanged
        assert (
            idea.creator_email == original_email
        ), f"Email should still be '{original_email}', got '{idea.creator_email}'"
        assert (
            idea.creator_phone == original_phone
        ), f"Phone should still be '{original_phone}', got '{idea.creator_phone}'"
        assert (
            idea.creator_contact_consent == original_consent
        ), f"Consent should still be {original_consent}, got {idea.creator_contact_consent}"

        # Other fields should be updated
        assert idea.name == "Brand New Idea Name"
        assert idea.description == "This is a completely updated description"


@pytest.mark.django_db
def test_creator_contact_fields_are_not_required_in_update_form(
    client, phase_factory, idea_factory
):
    """Test that creator contact fields are optional and can be left empty."""
    phase, module, project, idea = setup_phase(
        phase_factory, idea_factory, phases.IssuePhase
    )

    user = idea.creator
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "year": idea.created.year,
            "pk": idea.pk,
        },
    )

    with freeze_phase(phase):
        client.login(username=user.email, password="password")

        # Get the form and check field requirements
        response = client.get(url)
        form = response.context["form"]

        assert form.fields["creator_email"].required is False
        assert form.fields["creator_phone"].required is False
        assert form.fields["creator_contact_consent"].required is False


@pytest.mark.django_db
def test_existing_contact_fields_cleared_when_consent_removed_on_update(
    client, phase_factory, idea_factory
):
    """Test that when user unchecks consent during update, email and phone are cleared.

    Business rule: If user had previously provided contact info but then
    unchecks consent, the email and phone should be cleared from the database.
    """
    phase, module, project, idea = setup_phase(
        phase_factory, idea_factory, phases.IssuePhase
    )

    # Set initial contact values WITH consent
    idea.creator_email = "existing@example.com"
    idea.creator_phone = "+49123456789"
    idea.creator_contact_consent = True
    idea.save()

    user = idea.creator
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "year": idea.created.year,
            "pk": idea.pk,
        },
    )

    with freeze_phase(phase):
        client.login(username=user.email, password="password")

        # Update: uncheck consent, but still submit email/phone (they should be ignored)
        update_data = {
            "name": idea.name,
            "description": idea.description,
            "creator_email": "shouldbeignored@example.com",  # Should be ignored
            "creator_phone": "+9999999999",  # Should be ignored
            "creator_contact_consent": False,  # Consent removed
            "organisation_terms_of_use": True,
        }

        if idea.category:
            update_data["category"] = idea.category.pk

        response = client.post(url, update_data)
        assert response.status_code == 302
        assert redirect_target(response) == "idea-detail"

        idea.refresh_from_db()

        # Email and phone should be cleared because consent is False
        assert idea.creator_email == "", "Email should be cleared when consent removed"
        assert idea.creator_phone == "", "Phone should be cleared when consent removed"
        assert idea.creator_contact_consent is False, "Consent should be False"
