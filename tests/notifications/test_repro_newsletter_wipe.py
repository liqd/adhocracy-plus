"""Reproduction: saving the profile must not silently clear get_newsletters."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_profile_save_keeps_newsletter_optin(client, user):
    """A user who opted in to newsletters must stay opted in after an
    unrelated profile edit (the profile page does not render the field)."""
    user.get_newsletters = True
    user.save()
    client.login(email=user.email, password="password")

    # POST exactly what the profile template renders (no get_newsletters field)
    response = client.post(
        reverse("account_profile"),
        {
            "username": user.username,
            "bio": "Updated my bio",
            "twitter_handle": "",
            "facebook_handle": "",
            "homepage": "",
            "language": "en",
        },
    )

    assert response.status_code == 302
    user.refresh_from_db()
    assert (
        user.get_newsletters is True
    ), "profile save silently reset get_newsletters to False"
