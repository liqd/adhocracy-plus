import os

import pytest
from django.conf import settings

from tests import helpers


@pytest.mark.django_db
def test_delete_user_signal(user_factory, ImagePNG):
    user = user_factory(_avatar=ImagePNG)
    image_path = os.path.join(settings.MEDIA_ROOT, user._avatar.path)

    assert os.path.isfile(image_path)

    user.delete()
    assert not os.path.isfile(image_path)


@pytest.mark.django_db
def test_image_deleted_after_update(user_factory, ImagePNG):
    user = user_factory(_avatar=ImagePNG)
    image_path = os.path.join(settings.MEDIA_ROOT, user._avatar.path)
    thumbnail_path = helpers.createThumbnail(user._avatar)

    assert os.path.isfile(image_path)
    assert os.path.isfile(thumbnail_path)

    user._avatar = None
    user.save()

    assert not os.path.isfile(image_path)
    assert not os.path.isfile(thumbnail_path)


@pytest.mark.django_db
def test_absolute_url(client, user):
    url = user.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['user'] == user


@pytest.mark.django_db
def test_short_name(user):
    assert user.get_short_name() == user.username


@pytest.mark.django_db
def test_full_name(user):
    assert user.get_full_name() == \
        ('%s <%s>' % (user.username, user.email)).strip()
