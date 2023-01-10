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
