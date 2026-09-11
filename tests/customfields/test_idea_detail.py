import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

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
    CustomFieldAnswer.objects.create(
        content_object=idea, field=open_field, value="Kreuzberg"
    )
    CustomFieldAnswer.objects.create(
        content_object=idea, field=choice_field, value=str(choice_1.pk)
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


@pytest.mark.django_db
def test_detail_page_shows_unanswered_fields_with_placeholder(
    client, bs_module, idea_factory, custom_field_factory
):
    """Every configured question is shown, unanswered ones with a placeholder.

    Adresses the previous behaviour where only answered questions were
    visible on the posted idea.
    """
    module = bs_module
    settings = module.customfieldsettings_settings
    answered_field = custom_field_factory(
        settings=settings, type=CustomFieldType.OPEN, required=False
    )
    unanswered_field = custom_field_factory(
        settings=settings, type=CustomFieldType.OPEN, required=False
    )

    idea = idea_factory(module=module)
    CustomFieldAnswer.objects.create(
        content_object=idea, field=answered_field, value="Kreuzberg"
    )

    response = client.get(idea.get_absolute_url())
    assert response.status_code == 200
    content = response.content.decode()
    assert "item-detail__custom-fields" in content
    assert answered_field.label in content
    assert "Kreuzberg" in content
    assert unanswered_field.label in content
    assert "\u2014" in content


@pytest.mark.django_db
def test_detail_page_queries_do_not_scale_with_answers(
    client,
    bs_module,
    idea_factory,
    custom_field_factory,
    custom_field_choice_factory,
):
    def render_choice_queries(num_answers):
        settings = bs_module.customfieldsettings_settings
        fields = [
            custom_field_factory(
                settings=settings, type=CustomFieldType.CHOICE, required=False
            )
            for _ in range(num_answers)
        ]
        for index, field in enumerate(fields):
            custom_field_choice_factory(field=field, label=f"Option {index}")

        idea = idea_factory(module=bs_module)
        for field in fields:
            choice = field.choices.first()
            CustomFieldAnswer.objects.create(
                content_object=idea, field=field, value=str(choice.pk)
            )

        url = idea.get_absolute_url()
        with CaptureQueriesContext(connection) as ctx:
            response = client.get(url)
            assert response.status_code == 200
        return len(
            [
                query
                for query in ctx.captured_queries
                if "customfields_customfieldchoice" in query["sql"]
            ]
        )

    assert render_choice_queries(2) == render_choice_queries(6)
