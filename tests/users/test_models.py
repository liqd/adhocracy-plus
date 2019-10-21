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
