import base64
from io import BytesIO

import pytest
from django.urls import reverse
from PIL import Image

from adhocracy4.test.helpers import redirect_target
from apps.organisations.forms import SOCIAL_MEDIA_CHOICES
from apps.organisations.forms import SOCIAL_MEDIA_SIZES
from apps.organisations.views import DashboardCommunicationContentCreateView


@pytest.mark.django_db
def test_project_choice_view(client, user, organisation, project_factory):
    initiator = organisation.initiators.first()
    url = reverse(
        "a4dashboard:communication-content",
        kwargs={"organisation_slug": organisation.slug},
    )
    project1 = project_factory(organisation=organisation)
    project2 = project_factory(organisation=organisation)
    project3 = project_factory()
    response = client.get(url)
    assert response.status_code == 302
    client.login(username=user, password="password")
    response = client.get(url)
    assert response.status_code == 403
    client.login(username=initiator, password="password")
    response = client.get(url)
    assert response.status_code == 200
    assert "project_form" in response.context_data
    assert "content_form" not in response.context_data

    project_form = response.context_data["project_form"]
    assert "project" in project_form.fields
    assert "format" in project_form.fields

    project_choices = project_form.fields["project"].choices.queryset
    assert project1 in project_choices
    assert project2 in project_choices
    assert project3 not in project_choices

    assert project_form.fields["format"].choices == SOCIAL_MEDIA_CHOICES

    data = {"project": project1.pk, "format": SOCIAL_MEDIA_CHOICES[0][0]}
    redirect = client.post(url, data)
    assert redirect.status_code == 302
    assert redirect_target(redirect) == "communication-content-create"

    response = client.get(redirect.url)
    assert response.status_code == 200
    assert "content_form" in response.context_data


@pytest.mark.django_db
def test_content_create_view(
    client, user, organisation, project_factory, image_factory
):
    initiator = organisation.initiators.first()
    project = project_factory(organisation=organisation)
    format = SOCIAL_MEDIA_CHOICES[0][0]

    url = reverse(
        "a4dashboard:communication-content-create",
        kwargs={
            "organisation_slug": organisation.slug,
            "project_slug": project.slug,
            "format": format,
        },
    )

    response = client.get(url)
    assert response.status_code == 302

    client.login(username=user, password="password")
    response = client.get(url)
    assert response.status_code == 403

    client.login(username=initiator, password="password")
    response = client.get(url)
    assert response.status_code == 200

    assert "project_form" in response.context_data
    assert "content_form" in response.context_data

    content_form = response.context_data["content_form"]
    assert "title" in content_form.fields
    assert "description" in content_form.fields


@pytest.mark.django_db
def test_valid_data_sharepic_created(
    client, organisation, project_factory, image_factory
):
    initiator = organisation.initiators.first()
    organisation.logo = image_factory()
    organisation.save()
    project = project_factory(organisation=organisation)

    data = {
        "title": "my title",
        "description": "my description",
        "add_aplus_logo": True,
        "add_orga_logo": True,
    }

    client.login(username=initiator, password="password")

    for choice in SOCIAL_MEDIA_CHOICES:
        format = choice[0]
        sizes = SOCIAL_MEDIA_SIZES[format]
        data["image"] = image_factory(sizes["img_min_width"], sizes["img_min_height"])
        url = reverse(
            "a4dashboard:communication-content-create",
            kwargs={
                "organisation_slug": organisation.slug,
                "project_slug": project.slug,
                "format": format,
            },
        )

        response = client.post(url, data)
        assert response.status_code == 200
        assert "image_preview" in response.context_data
        assert "Refresh" in response.content.decode()
        assert "Download" in response.content.decode()
        preview_image_data = response.context_data["image_preview"]
        preview_image = Image.open(BytesIO(base64.b64decode(preview_image_data)))
        assert preview_image.size == (sizes["img_min_width"], sizes["overall_height"])


@pytest.mark.django_db
def test_invalid_data_no_sharepic_created(
    client, organisation, project_factory, image_factory
):
    initiator = organisation.initiators.first()
    project = project_factory(organisation=organisation)
    format = SOCIAL_MEDIA_CHOICES[0][0]

    url = reverse(
        "a4dashboard:communication-content-create",
        kwargs={
            "organisation_slug": organisation.slug,
            "project_slug": project.slug,
            "format": format,
        },
    )

    data = {"description": "my description", "image": image_factory()}

    client.login(username=initiator, password="password")
    response = client.post(url, data)
    assert response.status_code == 200
    assert "image_preview" not in response.context_data
    assert "Refresh" not in response.content.decode()
    assert "Download" not in response.content.decode()
    assert "title" in response.context_data["content_form"].errors


def test_sharepic_aspect_ratio():
    width = 1920
    height = 1080
    # 1080x760
    sharepic_format = SOCIAL_MEDIA_SIZES[1]
    req_width = sharepic_format["img_min_width"]
    req_height = sharepic_format["img_min_height"]
    required_ratio = req_width / float(req_height)
    resize = DashboardCommunicationContentCreateView.calc_aspect_ratio(
        width, height, req_width, req_height
    )
    new_ratio = (resize[2] - resize[0]) / float(resize[3] - resize[1])
    assert int(required_ratio) == int(new_ratio)
    # 1080x1278
    sharepic_format = SOCIAL_MEDIA_SIZES[2]
    req_width = sharepic_format["img_min_width"]
    req_height = sharepic_format["img_min_height"]
    required_ratio = req_width / float(req_height)
    resize = DashboardCommunicationContentCreateView.calc_aspect_ratio(
        width, height, req_width, req_height
    )
    new_ratio = (resize[2] - resize[0]) / float(resize[3] - resize[1])
    assert int(required_ratio) == int(new_ratio)
    # 1104x482
    sharepic_format = SOCIAL_MEDIA_SIZES[3]
    req_width = sharepic_format["img_min_width"]
    req_height = sharepic_format["img_min_height"]
    required_ratio = req_width / float(req_height)
    resize = DashboardCommunicationContentCreateView.calc_aspect_ratio(
        width, height, req_width, req_height
    )
    new_ratio = (resize[2] - resize[0]) / float(resize[3] - resize[1])
    assert int(required_ratio) == int(new_ratio)
    # different image size
    width = 1600
    height = 2560
    sharepic_format = SOCIAL_MEDIA_SIZES[1]
    req_width = sharepic_format["img_min_width"]
    req_height = sharepic_format["img_min_height"]
    required_ratio = req_width / float(req_height)
    resize = DashboardCommunicationContentCreateView.calc_aspect_ratio(
        width, height, req_width, req_height
    )
    new_ratio = (resize[2] - resize[0]) / float(resize[3] - resize[1])
    assert int(required_ratio) == int(new_ratio)
