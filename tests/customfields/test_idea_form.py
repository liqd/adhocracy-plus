import pytest
from django.urls import reverse

from adhocracy4.test.helpers import assert_template_response
from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import redirect_target
from apps.customfields.models import CustomFieldAnswer
from apps.customfields.models import CustomFieldType
from apps.ideas import models as idea_models


@pytest.mark.django_db
def test_create_idea_with_custom_fields(
    client,
    bs_module,
    user,
    category_factory,
    custom_field_factory,
    custom_field_choice_factory,
):
    module = bs_module
    phase = module.phase_set.first()
    settings = module.customfieldsettings_settings
    open_field = custom_field_factory(
        settings=settings, type=CustomFieldType.OPEN, required=True
    )
    choice_field = custom_field_factory(
        settings=settings, type=CustomFieldType.CHOICE, required=False
    )
    choice_1 = custom_field_choice_factory(field=choice_field, label="18-30")
    custom_field_choice_factory(field=choice_field, label="31-60")
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        response = client.get(url)
        assert_template_response(response, "a4_candy_ideas/idea_create_form.html")

        idea = {
            "name": "Idea",
            "description": "description",
            "category": category.pk,
            "organisation_terms_of_use": True,
            "custom_field_{}".format(open_field.pk): "",
        }
        response = client.post(url, idea)
        assert response.status_code == 200
        assert not idea_models.Idea.objects.filter(name="Idea").exists()

        idea["custom_field_{}".format(open_field.pk)] = "Kreuzberg"
        idea["custom_field_{}".format(choice_field.pk)] = str(choice_1.pk)
        response = client.post(url, idea)
        assert redirect_target(response) == "idea-detail"

        created = idea_models.Idea.objects.get(name="Idea")
        answers = created.custom_field_answers.all()
        assert answers.count() == 2
        assert answers.get(field=open_field).value == "Kreuzberg"
        assert answers.get(field=choice_field).value == str(choice_1.pk)


@pytest.mark.django_db
def test_required_choice_field_is_enforced(
    client,
    bs_module,
    user,
    category_factory,
    custom_field_factory,
    custom_field_choice_factory,
):
    module = bs_module
    phase = module.phase_set.first()
    settings = module.customfieldsettings_settings
    choice_field = custom_field_factory(
        settings=settings, type=CustomFieldType.CHOICE, required=True
    )
    custom_field_choice_factory(field=choice_field, label="Option 1")
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        idea = {
            "name": "Idea",
            "description": "description",
            "category": category.pk,
            "organisation_terms_of_use": True,
        }
        response = client.post(url, idea)
        assert response.status_code == 200
        assert not idea_models.Idea.objects.filter(name="Idea").exists()


@pytest.mark.django_db
def test_create_idea_without_settings_has_no_custom_fields(
    client, phase_factory, user, category_factory
):
    from adhocracy4.test.helpers import setup_phase
    from apps.ideas import phases

    phase, module, project, _ = setup_phase(phase_factory, None, phases.IssuePhase)
    module.blueprint_type = "BS"
    module.save()
    url = reverse(
        "a4_candy_ideas:idea-create",
        kwargs={
            "organisation_slug": module.project.organisation.slug,
            "module_slug": module.slug,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        response = client.get(url)
        form = response.context_data["form"]
        assert form.custom_fields == []


@pytest.mark.django_db
def test_update_idea_prefills_and_saves_custom_fields(
    client,
    bs_module,
    idea_factory,
    category_factory,
    custom_field_factory,
    custom_field_choice_factory,
):
    module = bs_module
    phase = module.phase_set.first()
    settings = module.customfieldsettings_settings
    open_field = custom_field_factory(
        settings=settings, type=CustomFieldType.OPEN, required=False
    )
    choice_field = custom_field_factory(
        settings=settings, type=CustomFieldType.CHOICE, required=False
    )
    choice_1 = custom_field_choice_factory(field=choice_field, label="Option 1")
    choice_2 = custom_field_choice_factory(field=choice_field, label="Option 2")

    idea = idea_factory(module=module)
    user = idea.creator
    CustomFieldAnswer.objects.create(
        content_object=idea, field=open_field, value="Kreuzberg"
    )
    CustomFieldAnswer.objects.create(
        content_object=idea, field=choice_field, value=str(choice_1.pk)
    )
    open_created = idea.custom_field_answers.get(field=open_field).created
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": idea.project.organisation.slug,
            "pk": idea.pk,
            "year": idea.created.year,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        response = client.get(url)
        form = response.context_data["form"]
        assert form.fields["custom_field_{}".format(open_field.pk)].initial == (
            "Kreuzberg"
        )
        assert form.fields["custom_field_{}".format(choice_field.pk)].initial == (
            str(choice_1.pk)
        )

        data = {
            "name": idea.name,
            "description": idea.description,
            "category": category.pk,
            "organisation_terms_of_use": True,
            "custom_field_{}".format(open_field.pk): "Friedrichshain",
            "custom_field_{}".format(choice_field.pk): str(choice_2.pk),
        }
        response = client.post(url, data)
        assert redirect_target(response) == "idea-detail"

        idea.refresh_from_db()
        answers = idea.custom_field_answers.all()
        assert answers.get(field=open_field).value == "Friedrichshain"
        assert answers.get(field=choice_field).value == str(choice_2.pk)
        # update_or_create keeps the original created timestamp
        assert answers.get(field=open_field).created == open_created


@pytest.mark.django_db
def test_update_idea_clears_custom_field_answer(
    client,
    bs_module,
    idea_factory,
    category_factory,
    custom_field_factory,
):
    module = bs_module
    phase = module.phase_set.first()
    settings = module.customfieldsettings_settings
    open_field = custom_field_factory(
        settings=settings, type=CustomFieldType.OPEN, required=False
    )

    idea = idea_factory(module=module)
    user = idea.creator
    CustomFieldAnswer.objects.create(
        content_object=idea, field=open_field, value="Kreuzberg"
    )
    category = category_factory(module=module)
    url = reverse(
        "a4_candy_ideas:idea-update",
        kwargs={
            "organisation_slug": idea.project.organisation.slug,
            "pk": idea.pk,
            "year": idea.created.year,
        },
    )
    with freeze_phase(phase):
        client.login(username=user.email, password="password")
        data = {
            "name": idea.name,
            "description": idea.description,
            "category": category.pk,
            "organisation_terms_of_use": True,
            "custom_field_{}".format(open_field.pk): "",
        }
        response = client.post(url, data)
        assert redirect_target(response) == "idea-detail"

        idea.refresh_from_db()
        assert idea.custom_field_answers.count() == 0
