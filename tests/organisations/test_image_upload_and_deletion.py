from pathlib import Path

import pytest
from django.urls import reverse

from adhocracy4.projects.models import Project


@pytest.mark.django_db
def test_organisation_image_upload_and_deletion(
    client, organisation_factory, project_factory, image_png, small_image
):

    organisation = organisation_factory(image=image_png, logo=small_image)
    project = project_factory(
        organisation=organisation, image=image_png, tile_image=small_image
    )
    image_path = Path(organisation.image.path)
    logo_path = Path(organisation.logo.path)
    initiator = organisation.initiators.first()

    assert "organisations/backgrounds" in organisation.image.path
    assert "organisations/logos" in organisation.logo.path

    # check organisation images are not deleted when project is deleted
    client.login(username=initiator.email, password="password")

    url = reverse(
        "project-delete",
        kwargs={"organisation_slug": project.organisation.slug, "pk": project.pk},
    )
    client.post(url)

    count = Project.objects.all().count()
    assert count == 0
    assert image_path.exists()
    assert logo_path.exists()

    # check organisation images are not deleted when initiator is deleted
    url = reverse("account_deletion")

    client.post(
        url,
        {
            "password": "password",
        },
    )

    assert image_path.exists()
    assert logo_path.exists()

    # check organisation images are deleted when organisation is deleted
    organisation.delete()
    assert not image_path.exists()
    assert not logo_path.exists()


@pytest.mark.django_db
def test_image_deleted_after_update(organisation_factory, image_png, small_image):
    organisation = organisation_factory(image=image_png, logo=small_image)
    image_path = Path(organisation.image.path)
    logo_path = Path(organisation.logo.path)

    assert "organisations/backgrounds" in organisation.image.path
    assert "organisations/logos" in organisation.logo.path

    organisation.image = None
    organisation.save()

    assert not image_path.exists()
    assert logo_path.exists()
