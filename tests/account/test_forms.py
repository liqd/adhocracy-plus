import pytest

from apps.account import forms


@pytest.mark.django_db
def test_clean_username(user_factory):
    user = user_factory(
        username='username'
    )
    data = {
        'username': 'UserName',
        'get_notifications': 'on',
        'get_newsletters': 'on',
        'bio': 'This is me!',
        'twitter_handle': 'Birdybird',
        'facebook_handle': 'Birdybird',
        'homepage': 'http://example.com/',
        'language': 'en',
    }
    form = forms.ProfileForm(data=data)
    assert not form.is_valid()
    assert (form['username'].errors[0].
            startswith('A user with that username'))

    data = {
        'username': user.email,
        'get_notifications': 'on',
        'get_newsletters': 'on',
        'bio': 'This is me!',
        'twitter_handle': 'Birdybird',
        'facebook_handle': 'Birdybird',
        'homepage': 'http://example.com/',
        'language': 'en',
    }
    form = forms.ProfileForm(data=data)
    assert not form.is_valid()
    assert (form['username'].errors[0].
            startswith('This username is invalid.'))
