from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from adhocracy4.projects.models import Project


@pytest.mark.django_db
def test_project_image_deleted_when_project_is_deleted(
    client, project_factory, image_png, small_image
):

    project = project_factory(image=image_png, tile_image=small_image)
    initiator = project.organisation.initiators.first()
    image_path = Path(project.image.path)
    tile_path = Path(project.tile_image.path)

    assert "projects/backgrounds" in project.image.path
    assert "projects/tiles" in project.tile_image.path

    client.login(username=initiator.email, password="password")
    url = reverse(
        "project-delete",
        kwargs={"organisation_slug": project.organisation.slug, "pk": project.pk},
    )
    client.post(url)

    count = Project.objects.all().count()
    assert count == 0
    assert not image_path.exists()
    assert not tile_path.exists()


@pytest.mark.django_db
def test_project_image_not_deleted_when_initiator_is_deleted(
    client, project_factory, image_png, small_image
):
    User = get_user_model()

    project = project_factory(image=image_png, tile_image=small_image)
    initiator = project.organisation.initiators.first()
    image_path = Path(project.image.path)
    tile_path = Path(project.tile_image.path)

    assert "projects/backgrounds" in project.image.path
    assert "projects/tiles" in project.tile_image.path

    client.login(username=initiator.email, password="password")
    url = reverse("account_deletion")

    client.post(
        url,
        {
            "password": "password",
        },
    )

    assert image_path.exists()
    assert tile_path.exists()

    count = Project.objects.all().count()
    assert count == 1
    with pytest.raises(User.DoesNotExist):
        User.objects.get(email=initiator.email)


@pytest.mark.django_db
def test_image_deleted_after_update(project_factory, image_png, small_image):
    project = project_factory(image=image_png, tile_image=small_image)
    image_path = Path(project.image.path)
    tile_path = Path(project.tile_image.path)

    assert "projects/backgrounds" in project.image.path
    assert "projects/tiles" in project.tile_image.path

    project.image = None
    project.save()

    assert not image_path.exists()
    assert tile_path.exists()
