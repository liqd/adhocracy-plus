import pytest
from django.urls import reverse

from apps.account import forms


@pytest.mark.django_db
def test_clean_username(user_factory):
    user = user_factory(username="username")
    data = {
        "username": "UserName",
        "get_notifications": "on",
        "get_newsletters": "on",
        "bio": "This is me!",
        "twitter_handle": "Birdybird",
        "facebook_handle": "Birdybird",
        "homepage": "http://example.com/",
        "language": "en",
    }
    form = forms.ProfileForm(data=data)
    assert not form.is_valid()
    assert form["username"].errors[0].startswith("A user with that username")

    data = {
        "username": user.email,
        "get_notifications": "on",
        "get_newsletters": "on",
        "bio": "This is me!",
        "twitter_handle": "Birdybird",
        "facebook_handle": "Birdybird",
        "homepage": "http://example.com/",
        "language": "en",
    }
    form = forms.ProfileForm(data=data)
    assert not form.is_valid()
    assert form["username"].errors[0].startswith("This username is invalid.")


@pytest.mark.django_db
def test_get_terms_of_use_label(organisation_terms_of_use_factory, user, client):
    terms_1 = organisation_terms_of_use_factory(user=user, has_agreed=True)
    client.login(email=user.email, password="password")
    url = reverse("user_agreements")

    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context["formset"]) == 1

    label = response.context["formset"].forms[0].fields["has_agreed"].label
    terms_url = reverse(
        "organisation-terms-of-use",
        kwargs={"organisation_slug": terms_1.organisation.slug},
    )
    assert label.startswith("Yes, I have read and agree to")
    assert ('<a href="' + terms_url + '" target="_blank">terms of use</a>') in label
