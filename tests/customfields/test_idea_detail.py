import pytest

from apps.customfields.models import CustomFieldAnswer
from apps.customfields.models import CustomFieldType


@pytest.mark.django_db
def test_detail_page_shows_custom_field_answers(
    client,
    bs_module,
    idea_factory,
    custom_field_factory,
    custom_field_choice_factory,
):
    module = bs_module
    settings = module.customfieldsettings_settings
    open_field = custom_field_factory(
        settings=settings, type=CustomFieldType.OPEN, required=False
    )
    choice_field = custom_field_factory(
        settings=settings, type=CustomFieldType.CHOICE, required=False
    )
    choice_1 = custom_field_choice_factory(field=choice_field, label="Option 1")

    idea = idea_factory(module=module)
    CustomFieldAnswer.objects.create(idea=idea, field=open_field, value="Kreuzberg")
    CustomFieldAnswer.objects.create(
        idea=idea, field=choice_field, value=str(choice_1.pk)
    )

    url = idea.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    assert open_field.label in content
    assert "Kreuzberg" in content
    assert choice_field.label in content
    assert "Option 1" in content


@pytest.mark.django_db
def test_detail_page_without_answers_shows_no_custom_fields_section(
    client, bs_module, idea_factory
):
    idea = idea_factory(module=bs_module)
    url = idea.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200
    assert "item-detail__custom-fields" not in response.content.decode()
