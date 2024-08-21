from pathlib import Path

import pytest


@pytest.mark.django_db
def test_extrafields_image_upload_and_deletion(
    user, interactive_extra_fields_factory, image_png
):
    module = interactive_extra_fields_factory(event_image=image_png, creator=user)
    image_path = Path(module.event_image.path)
    assert "interactiveevents/images" in module.event_image.path

    module.delete()
    assert not image_path.exists()


@pytest.mark.django_db
def test_image_deleted_after_update(user, interactive_extra_fields_factory, image_png):
    module = interactive_extra_fields_factory(event_image=image_png, creator=user)
    image_path = Path(module.event_image.path)
    assert "interactiveevents/images" in module.event_image.path

    module.event_image = None
    module.save()
    assert not image_path.exists()
