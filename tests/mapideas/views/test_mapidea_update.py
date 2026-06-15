import pytest
from django.urls import reverse

from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import redirect_target
from adhocracy4.test.helpers import setup_phase
from apps.mapideas import models
from apps.mapideas import phases


@pytest.mark.django_db
def test_creator_can_update_during_active_phase(
    client, phase_factory, map_idea_factory, category_factory, area_settings_factory
):
    phase, module, project, mapidea = setup_phase(
        phase_factory, map_idea_factory, phases.IssuePhase
    )
    area_settings_factory(module=module)
    category = category_factory(module=module)
    user = mapidea.creator
    url = reverse(
        "a4_candy_mapideas:mapidea-update",
        kwargs={
            "organisation_slug": mapidea.project.organisation.slug,
            "pk": mapidea.pk,
            "year": mapidea.created.year,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        data = {
            "name": "Another MapIdea",
            "description": "changed description",
            "category": category.pk,
            "point": (0, 0),
            "point_label": "somewhere",
            "organisation_terms_of_use": True,
        }
        response = client.post(url, data)
        assert redirect_target(response) == "mapidea-detail"
        assert response.status_code == 302
        updated_mapidea = models.MapIdea.objects.get(id=mapidea.pk)
        assert updated_mapidea.description == "changed description"


@pytest.mark.django_db
def test_creator_cannot_update_in_wrong_phase(
    client, phase_factory, map_idea_factory, category_factory
):
    phase, module, project, mapidea = setup_phase(
        phase_factory, map_idea_factory, phases.RatingPhase
    )
    category = category_factory(module=module)
    user = mapidea.creator
    assert user not in project.moderators.all()
    url = reverse(
        "a4_candy_mapideas:mapidea-update",
        kwargs={
            "organisation_slug": mapidea.project.organisation.slug,
            "pk": mapidea.pk,
            "year": mapidea.created.year,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        data = {
            "name": "Another MapIdea",
            "description": "changed description",
            "category": category.pk,
            "organisation_terms_of_use": True,
        }
        response = client.post(url, data)
        assert response.status_code == 403


@pytest.mark.django_db
def test_moderator_can_update_during_wrong_phase(
    client, phase_factory, map_idea_factory, category_factory, area_settings_factory
):
    phase, module, project, mapidea = setup_phase(
        phase_factory, map_idea_factory, phases.RatingPhase
    )
    area_settings_factory(module=module)
    category = category_factory(module=module)
    user = mapidea.creator
    moderator = project.moderators.first()
    assert moderator is not user
    url = reverse(
        "a4_candy_mapideas:mapidea-update",
        kwargs={
            "organisation_slug": mapidea.project.organisation.slug,
            "pk": mapidea.pk,
            "year": mapidea.created.year,
        },
    )
    with freeze_phase(phase):
        client.login(username=moderator.email, password="password")
        data = {
            "name": "Another MapIdea",
            "description": "changed description",
            "category": category.pk,
            "point": (0, 0),
            "point_label": "somewhere else",
            "organisation_terms_of_use": True,
        }
        response = client.post(url, data)
        assert redirect_target(response) == "mapidea-detail"
        assert response.status_code == 302
        updated_mapidea = models.MapIdea.objects.get(id=mapidea.pk)
        assert updated_mapidea.description == "changed description"


@pytest.mark.django_db
def test_creator_cannot_update(client, map_idea_factory):
    mapidea = map_idea_factory()
    user = mapidea.creator
    assert user not in mapidea.module.project.moderators.all()
    url = reverse(
        "a4_candy_mapideas:mapidea-update",
        kwargs={
            "organisation_slug": mapidea.project.organisation.slug,
            "pk": mapidea.pk,
            "year": mapidea.created.year,
        },
    )
    client.login(username=user.email, password="password")
    data = {
        "name": "Another MapIdea",
        "description": "changed description",
        "organisation_terms_of_use": True,
    }
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_moderators_can_always_update(
    client, phase_factory, map_idea_factory, category_factory, area_settings_factory
):
    phase, module, project, mapidea = setup_phase(
        phase_factory, map_idea_factory, phases.RatingPhase
    )
    area_settings_factory(module=module)
    category = category_factory(module=module)
    user = mapidea.creator
    moderator = project.moderators.first()
    assert moderator is not user
    url = reverse(
        "a4_candy_mapideas:mapidea-update",
        kwargs={
            "organisation_slug": mapidea.project.organisation.slug,
            "pk": mapidea.pk,
            "year": mapidea.created.year,
        },
    )
    client.login(username=moderator.email, password="password")
    data = {
        "name": "Another MapIdea",
        "description": "changed description",
        "category": category.pk,
        "point": (0, 0),
        "point_label": "somewhere",
        "organisation_terms_of_use": True,
    }
    response = client.post(url, data)
    assert redirect_target(response) == "mapidea-detail"
    assert response.status_code == 302
    updated_mapidea = models.MapIdea.objects.get(id=mapidea.pk)
    assert updated_mapidea.description == "changed description"


@pytest.mark.django_db
def test_moderators_can_update_only_with_terms_agreement(
    client, map_idea_factory, organisation_terms_of_use_factory, area_settings_factory
):
    mapidea = map_idea_factory()
    area_settings_factory(module=mapidea.module)
    moderator = mapidea.module.project.moderators.first()
    assert moderator is not mapidea.creator
    url = reverse(
        "a4_candy_mapideas:mapidea-update",
        kwargs={
            "organisation_slug": mapidea.project.organisation.slug,
            "pk": mapidea.pk,
            "year": mapidea.created.year,
        },
    )
    client.login(username=moderator.email, password="password")
    data = {
        "name": "Another mappy Idea",
        "description": "changed description",
        "point": (0, 0),
    }
    response = client.post(url, data)
    assert response.status_code == 200

    organisation_terms_of_use_factory(
        user=moderator,
        organisation=mapidea.module.project.organisation,
        has_agreed=True,
    )
    response = client.post(url, data)
    assert redirect_target(response) == "mapidea-detail"
    assert response.status_code == 302
    updated_idea = models.MapIdea.objects.get(id=mapidea.pk)
    assert updated_idea.description == "changed description"


@pytest.mark.django_db
def test_creator_can_update_creator_contact_fields_on_mapidea(
    client, phase_factory, map_idea_factory, area_settings_factory
):
    """Test that user can update creator contact fields when editing a map idea."""
    phase, module, project, mapidea = setup_phase(
        phase_factory, map_idea_factory, phases.IssuePhase
    )
    area_settings_factory(module=module)

    # Get the actual creator of the map idea
    user = mapidea.creator

    # Set initial values
    mapidea.creator_email = "initial@example.com"
    mapidea.creator_phone = "+1111111111"
    mapidea.creator_contact_consent = False
    mapidea.save()

    url = reverse(
        "a4_candy_mapideas:mapidea-update",
        kwargs={
            "organisation_slug": mapidea.project.organisation.slug,
            "pk": mapidea.pk,
            "year": mapidea.created.year,
        },
    )

    with freeze_phase(phase):
        client.login(username=user.email, password="password")

        update_data = {
            "name": mapidea.name,
            "description": mapidea.description,
            "point": (0, 0),
            "point_label": "somewhere",
            "organisation_terms_of_use": True,
            "creator_email": "updated@example.com",
            "creator_phone": "+9876543210",
            "creator_contact_consent": True,
        }

        if mapidea.category:
            update_data["category"] = mapidea.category.pk

        response = client.post(url, update_data)
        assert response.status_code == 302
        assert redirect_target(response) == "mapidea-detail"

        mapidea.refresh_from_db()
        assert mapidea.creator_email == "updated@example.com"
        assert mapidea.creator_phone == "+9876543210"
        assert mapidea.creator_contact_consent is True


@pytest.mark.django_db
def test_mapidea_contact_fields_persist_when_updating_other_fields(
    client, phase_factory, map_idea_factory, area_settings_factory
):
    """Test that contact fields retain values when only other fields are updated."""
    phase, module, project, mapidea = setup_phase(
        phase_factory, map_idea_factory, phases.IssuePhase
    )
    area_settings_factory(module=module)

    # Set initial contact values
    original_email = "persist@example.com"
    original_phone = "+9999999999"
    original_consent = True

    mapidea.creator_email = original_email
    mapidea.creator_phone = original_phone
    mapidea.creator_contact_consent = original_consent
    mapidea.save()

    user = mapidea.creator
    url = reverse(
        "a4_candy_mapideas:mapidea-update",
        kwargs={
            "organisation_slug": mapidea.project.organisation.slug,
            "pk": mapidea.pk,
            "year": mapidea.created.year,
        },
    )

    with freeze_phase(phase):
        client.login(username=user.email, password="password")

        # Update ONLY name and description - do NOT include contact fields
        update_data = {
            "name": "Brand New MapIdea Name",
            "description": "This is a completely updated description",
            "point": (0, 0),
            "point_label": "somewhere",
            "organisation_terms_of_use": True,
        }

        if mapidea.category:
            update_data["category"] = mapidea.category.pk

        response = client.post(url, update_data)

        assert response.status_code == 302
        assert redirect_target(response) == "mapidea-detail"

        mapidea.refresh_from_db()

        # Contact fields should remain unchanged
        assert mapidea.creator_email == original_email
        assert mapidea.creator_phone == original_phone
        assert mapidea.creator_contact_consent == original_consent

        # Other fields should be updated
        assert mapidea.name == "Brand New MapIdea Name"
        assert mapidea.description == "This is a completely updated description"


@pytest.mark.django_db
def test_mapidea_contact_fields_cleared_when_consent_removed_on_update(
    client, phase_factory, map_idea_factory, area_settings_factory
):
    """Test that when user unchecks consent during update, email and phone are cleared."""
    phase, module, project, mapidea = setup_phase(
        phase_factory, map_idea_factory, phases.IssuePhase
    )
    area_settings_factory(module=module)

    # Set initial contact values WITH consent
    mapidea.creator_email = "existing@example.com"
    mapidea.creator_phone = "+49123456789"
    mapidea.creator_contact_consent = True
    mapidea.save()

    user = mapidea.creator
    url = reverse(
        "a4_candy_mapideas:mapidea-update",
        kwargs={
            "organisation_slug": mapidea.project.organisation.slug,
            "pk": mapidea.pk,
            "year": mapidea.created.year,
        },
    )

    with freeze_phase(phase):
        client.login(username=user.email, password="password")

        # Update: uncheck consent
        update_data = {
            "name": mapidea.name,
            "description": mapidea.description,
            "point": (0, 0),
            "point_label": "somewhere",
            "creator_email": "shouldbeignored@example.com",
            "creator_phone": "+9999999999",
            "creator_contact_consent": False,
            "organisation_terms_of_use": True,
        }

        if mapidea.category:
            update_data["category"] = mapidea.category.pk

        response = client.post(url, update_data)
        assert response.status_code == 302
        assert redirect_target(response) == "mapidea-detail"

        mapidea.refresh_from_db()

        # Email and phone should be cleared because consent is False
        assert mapidea.creator_email == ""
        assert mapidea.creator_phone == ""
        assert mapidea.creator_contact_consent is False


@pytest.mark.django_db
def test_mapidea_contact_fields_prepopulated_in_update_form(
    client, phase_factory, map_idea_factory, area_settings_factory
):
    """Test that MapIdea (inheriting from AbstractIdeaUpdateView) gets contact fields pre-populated."""
    phase, module, project, mapidea = setup_phase(
        phase_factory, map_idea_factory, phases.IssuePhase
    )
    area_settings_factory(module=module)

    # Set initial contact values
    mapidea.creator_email = "mapidea_prepop@example.com"
    mapidea.creator_phone = "+49111222333"
    mapidea.creator_contact_consent = True
    mapidea.save()

    user = mapidea.creator
    url = reverse(
        "a4_candy_mapideas:mapidea-update",
        kwargs={
            "organisation_slug": mapidea.project.organisation.slug,
            "pk": mapidea.pk,
            "year": mapidea.created.year,
        },
    )

    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        response = client.get(url)

        assert response.status_code == 200
        form = response.context["form"]

        # Verify inheritance works - MapIdea gets pre-populated values
        assert form.initial.get("creator_email") == "mapidea_prepop@example.com"
        assert form.initial.get("creator_phone") == "+49111222333"
        assert form.initial.get("creator_contact_consent") is True
