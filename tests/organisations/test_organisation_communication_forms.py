import pytest
from django.utils import translation

from apps.organisations.forms import SOCIAL_MEDIA_CHOICES
from apps.organisations.forms import SOCIAL_MEDIA_SIZES
from apps.organisations.forms import CommunicationContentCreationForm


@pytest.mark.django_db
def test_upload_image_validation(organisation, project_factory, image_factory):

    project = project_factory(organisation=organisation)
    data = {"title": "my title", "description": "my description"}

    for choice in SOCIAL_MEDIA_CHOICES:
        format = choice[0]
        min_width = SOCIAL_MEDIA_SIZES[format]["img_min_width"]
        min_height = SOCIAL_MEDIA_SIZES[format]["img_min_height"]
        valid_image = image_factory(min_width, min_height)
        invalid_image = image_factory(int(min_width * 0.8), int(min_height * 0.8))

        files_data = {"image": valid_image}
        content_form = CommunicationContentCreationForm(
            data=data, files=files_data, project=project, format=format
        )
        assert content_form.is_valid()

        files_data = {"image": invalid_image}
        content_form = CommunicationContentCreationForm(
            data=data, files=files_data, project=project, format=format
        )
        assert not content_form.is_valid()
        assert "image" in content_form.errors
        with translation.override("en_GB"):
            assert (
                "Image must be at least {} pixels wide".format(min_width)
                in content_form.errors["image"]
            )
            assert (
                "Image must be at least {} pixels high".format(min_height)
                in content_form.errors["image"]
            )


@pytest.mark.django_db
def test_content_create_initial_data(organisation, project_factory):

    project = project_factory(organisation=organisation)
    format = SOCIAL_MEDIA_CHOICES[0][0]
    title_max_length = SOCIAL_MEDIA_SIZES[format]["title_max_length"]
    description_max_length = SOCIAL_MEDIA_SIZES[format]["description_max_length"]

    content_form = CommunicationContentCreationForm(project=project, format=format)
    assert content_form.fields["title"].initial == project.name[:title_max_length]
    assert (
        content_form.fields["description"].initial
        == project.description[:description_max_length]
    )
    assert content_form.fields["add_aplus_logo"].initial
    assert content_form.fields["add_orga_logo"].initial
