from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from adhocracy4.test.helpers import redirect_target


@pytest.mark.django_db
def test_profile_edit(client, user):
    client.login(email=user.email, password="password")
    url = reverse("account_profile")

    response = client.post(
        url,
        {
            "username": user.username,
            "get_notifications": "on",
            "get_newsletters": "on",
            "bio": "This is me!",
            "twitter_handle": "Birdybird",
            "facebook_handle": "Birdybird",
            "homepage": "http://example.com/",
            "language": "en",
        },
    )

    assert response.status_code == 302

    profile_url = reverse("profile", kwargs={"slug": user.username})
    profile_response = client.get(profile_url)

    assert profile_response.status_code == 200
    assert profile_response.context["user"] == user
    assert profile_response.context["user"].twitter_handle == "Birdybird"


@pytest.mark.django_db
def test_organisation_terms_edit(
    client, user, organisation_factory, organisation_terms_of_use_factory
):
    organisation_1 = organisation_factory()
    organisation_2 = organisation_factory()
    terms_1 = organisation_terms_of_use_factory(
        user=user, organisation=organisation_1, has_agreed=True
    )
    terms_2 = organisation_terms_of_use_factory(
        user=user, organisation=organisation_2, has_agreed=False
    )

    client.login(email=user.email, password="password")
    url = reverse("user_agreements")

    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context["formset"]) == 2

    data = {
        "organisationtermsofuse_set-TOTAL_FORMS": "2",
        "organisationtermsofuse_set-INITIAL_FORMS": "2",
        "organisationtermsofuse_set-MIN_NUM_FORMS": "0",
        "organisationtermsofuse_set-MAX_NUM_FORMS": "1000",
        "organisationtermsofuse_set-0-has_agreed": "False",
        "organisationtermsofuse_set-0-id": terms_1.id,
        "organisationtermsofuse_set-0-user": user.id,
        "organisationtermsofuse_set-1-has_agreed": "True",
        "organisationtermsofuse_set-1-id": terms_2.id,
        "organisationtermsofuse_set-1-user": user.id,
    }

    response = client.post(url, data)

    assert response.status_code == 302
    assert redirect_target(response) == "user_agreements"
    terms_1.refresh_from_db()
    assert not terms_1.has_agreed
    terms_2.refresh_from_db()
    assert terms_2.has_agreed


@pytest.mark.django_db
@pytest.mark.parametrize("password", [None, "", "wrong_password"])
def test_account_deletion_invalid_password(client, user, password):
    User = get_user_model()
    pk = user.pk
    client.login(email=user.email, password="password")
    url = reverse("account_deletion")

    assert User.objects.count() == 1
    assert User.objects.filter(pk=pk).exists()
    if password is None:
        # test without data
        response = client.post(url)
    else:
        response = client.post(
            url,
            {
                "password": password,
            },
        )

    assert response.status_code == 200
    assert User.objects.count() == 1
    assert User.objects.filter(pk=pk).exists()
    assert len(mail.outbox) == 0
    form = response.context_data["form"]
    assert not form.is_valid()


@pytest.mark.django_db
def test_account_deletion(client, user):
    User = get_user_model()

    client.login(email=user.email, password="password")
    url = reverse("account_deletion")

    assert User.objects.count() == 1
    assert User.objects.filter(pk=user.pk).exists()

    response = client.post(
        url,
        {
            "password": "password",
        },
    )

    assert response.status_code == 302
    assert User.objects.count() == 0
    assert not User.objects.filter(pk=user.pk).exists()
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == (
        "Confirmation: Deletion of Your Account on " "adhocracy+"
    )
    # assert that user is redirected to homepage
    assert redirect_target(response) == "wagtail_serve"


@pytest.mark.django_db
def test_account_image_deletion(client, user_factory, small_image):
    User = get_user_model()
    user = user_factory(_avatar=small_image)
    image_path = Path(user._avatar.path)

    assert "users/images/" in user._avatar.path

    client.login(email=user.email, password="password")
    url = reverse("account_deletion")

    client.post(
        url,
        {
            "password": "password",
        },
    )
    assert User.objects.count() == 0
    assert not image_path.exists()
