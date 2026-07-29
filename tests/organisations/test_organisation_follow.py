import pytest
from django.urls import reverse

from apps.organisations.models import OrganisationFollow
from tests.helpers import GuestUserCreator


@pytest.mark.django_db
def test_organisation_follow_model_creation(organisation_factory, user_factory):
    organisation = organisation_factory()
    user = user_factory()

    follow = OrganisationFollow.objects.create(
        organisation=organisation,
        creator=user,
        enabled=True,
    )

    assert follow.organisation == organisation
    assert follow.creator == user
    assert follow.enabled is True
    assert str(follow) == "OrganisationFollow({}, enabled={})".format(
        organisation, True
    )


@pytest.mark.django_db
def test_organisation_follow_unique_constraint(organisation_factory, user_factory):
    organisation = organisation_factory()
    user = user_factory()

    OrganisationFollow.objects.create(
        organisation=organisation,
        creator=user,
        enabled=True,
    )

    with pytest.raises(Exception):
        OrganisationFollow.objects.create(
            organisation=organisation,
            creator=user,
            enabled=False,
        )


@pytest.mark.django_db
def test_organisation_follow_default_enabled(organisation_factory, user_factory):
    organisation = organisation_factory()
    user = user_factory()

    follow = OrganisationFollow.objects.create(
        organisation=organisation,
        creator=user,
    )

    assert follow.enabled is True


@pytest.mark.django_db
def test_organisation_follow_toggle_view_toggles(
    client, organisation_factory, user_factory
):
    organisation = organisation_factory()
    user = user_factory()
    client.force_login(user)

    url = reverse(
        "organisation-follow",
        kwargs={"organisation_slug": organisation.slug},
    )

    response = client.post(url)
    assert response.status_code == 200

    follow = OrganisationFollow.objects.get(organisation=organisation, creator=user)
    assert follow.enabled is True

    response = client.post(url)
    assert response.status_code == 200

    follow.refresh_from_db()
    assert follow.enabled is False


@pytest.mark.django_db
def test_organisation_follow_toggle_guest_user(client, organisation_factory):
    organisation = organisation_factory()
    guest_user = GuestUserCreator().create_guest_user()
    client.force_login(guest_user)

    url = reverse(
        "organisation-follow",
        kwargs={"organisation_slug": organisation.slug},
    )

    response = client.post(url)
    assert response.status_code == 200

    follow = OrganisationFollow.objects.filter(
        organisation=organisation, creator=guest_user
    )
    assert follow.count() == 1
    assert follow.first().enabled is True


@pytest.mark.django_db
def test_organisation_follow_toggle_view_unauthenticated(client, organisation_factory):
    organisation = organisation_factory()

    url = reverse(
        "organisation-follow",
        kwargs={"organisation_slug": organisation.slug},
    )

    response = client.post(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_organisation_unfollow_view_unfollows(
    client, organisation_factory, user_factory
):
    organisation = organisation_factory()
    user = user_factory()
    OrganisationFollow.objects.create(
        organisation=organisation,
        creator=user,
        enabled=True,
    )
    client.force_login(user)

    url = reverse(
        "organisation-unfollow",
        kwargs={"organisation_slug": organisation.slug},
    )

    response = client.get(url)
    assert response.status_code == 200

    follow = OrganisationFollow.objects.get(organisation=organisation, creator=user)
    assert follow.enabled is False


@pytest.mark.django_db
def test_organisation_unfollow_view_unauthenticated(client, organisation_factory):
    organisation = organisation_factory()

    url = reverse(
        "organisation-unfollow",
        kwargs={"organisation_slug": organisation.slug},
    )

    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_organisation_unfollow_view_noop_when_not_following(
    client, organisation_factory, user_factory
):
    organisation = organisation_factory()
    user = user_factory()
    client.force_login(user)

    url = reverse(
        "organisation-unfollow",
        kwargs={"organisation_slug": organisation.slug},
    )

    response = client.get(url)
    assert response.status_code == 200

    follows = OrganisationFollow.objects.filter(
        organisation=organisation, creator=user, enabled=True
    )
    assert follows.count() == 0
