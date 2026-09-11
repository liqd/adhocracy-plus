import pytest
from django.urls import reverse

from apps.customfields.models import CustomField
from apps.customfields.models import CustomFieldSettings
from apps.customfields.models import CustomFieldType

from .factories import CustomFieldSettingsFactory


@pytest.mark.django_db
def test_api_get_settings(apiclient, bs_module):
    settings = CustomFieldSettings.objects.get(module=bs_module)
    initiator = bs_module.project.organisation.initiators.first()
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=initiator)
    response = apiclient.get(url)
    assert response.status_code == 200
    assert response.data["fields"] == []


@pytest.mark.django_db
def test_api_get_denied_for_regular_user(apiclient, bs_module, user):
    settings = CustomFieldSettings.objects.get(module=bs_module)
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=user)
    response = apiclient.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_api_update_creates_fields_and_choices(apiclient, bs_module):
    settings = CustomFieldSettings.objects.get(module=bs_module)
    initiator = bs_module.project.organisation.initiators.first()
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=initiator)

    data = {
        "fields": [
            {"label": "Where do you live?", "type": "open", "required": True},
            {
                "label": "District",
                "type": "choice",
                "required": False,
                "choices": [{"label": "North"}, {"label": "South"}],
            },
        ]
    }
    response = apiclient.put(url, data, format="json")
    assert response.status_code == 200

    fields = settings.fields.all()
    assert fields.count() == 2
    open_field = fields.get(type=CustomFieldType.OPEN)
    assert open_field.label == "Where do you live?"
    assert open_field.required is True
    choice_field = fields.get(type=CustomFieldType.CHOICE)
    assert list(choice_field.choices.values_list("label", flat=True)) == [
        "North",
        "South",
    ]


@pytest.mark.django_db
def test_api_update_removes_deleted_fields(
    apiclient, bs_module, custom_field_factory, custom_field_choice_factory
):
    settings = CustomFieldSettings.objects.get(module=bs_module)
    field = custom_field_factory(settings=settings, type=CustomFieldType.CHOICE)
    custom_field_choice_factory(field=field, label="Option 1")
    initiator = bs_module.project.organisation.initiators.first()
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=initiator)

    response = apiclient.put(url, {"fields": []}, format="json")
    assert response.status_code == 200
    assert settings.fields.count() == 0
    assert not CustomField.objects.filter(pk=field.pk).exists()


@pytest.mark.django_db
def test_api_update_edits_existing_field(
    apiclient, bs_module, custom_field_factory, custom_field_choice_factory
):
    settings = CustomFieldSettings.objects.get(module=bs_module)
    field = custom_field_factory(settings=settings, type=CustomFieldType.CHOICE)
    choice = custom_field_choice_factory(field=field, label="Option 1")
    initiator = bs_module.project.organisation.initiators.first()
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=initiator)

    data = {
        "fields": [
            {
                "id": field.pk,
                "label": "New label",
                "type": "choice",
                "required": True,
                "choices": [{"id": choice.pk, "label": "Renamed"}],
            },
        ]
    }
    response = apiclient.put(url, data, format="json")
    assert response.status_code == 200

    field.refresh_from_db()
    assert field.label == "New label"
    assert field.required is True
    choice.refresh_from_db()
    assert choice.label == "Renamed"


@pytest.mark.django_db
def test_api_update_rejects_field_id_from_other_module(
    apiclient, bs_module, custom_field_factory
):
    settings = CustomFieldSettings.objects.get(module=bs_module)
    other_settings = CustomFieldSettingsFactory()
    foreign_field = custom_field_factory(
        settings=other_settings, label="Foreign", type=CustomFieldType.OPEN
    )
    initiator = bs_module.project.organisation.initiators.first()
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=initiator)

    data = {
        "fields": [
            {"id": foreign_field.pk, "label": "Hijacked", "type": "open"},
        ]
    }
    response = apiclient.put(url, data, format="json")
    assert response.status_code == 400

    foreign_field.refresh_from_db()
    assert foreign_field.settings == other_settings
    assert foreign_field.label == "Foreign"


@pytest.mark.django_db
def test_api_update_rejects_choice_id_from_other_field(
    apiclient, bs_module, custom_field_factory, custom_field_choice_factory
):
    settings = CustomFieldSettings.objects.get(module=bs_module)
    field = custom_field_factory(settings=settings, type=CustomFieldType.CHOICE)
    other_settings = CustomFieldSettingsFactory()
    other_field = custom_field_factory(
        settings=other_settings, type=CustomFieldType.CHOICE
    )
    foreign_choice = custom_field_choice_factory(field=other_field, label="Foreign")
    initiator = bs_module.project.organisation.initiators.first()
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=initiator)

    data = {
        "fields": [
            {
                "id": field.pk,
                "label": field.label,
                "type": "choice",
                "choices": [{"id": foreign_choice.pk, "label": "Stolen"}],
            },
        ]
    }
    response = apiclient.put(url, data, format="json")
    assert response.status_code == 400

    foreign_choice.refresh_from_db()
    assert foreign_choice.field == other_field
    assert foreign_choice.label == "Foreign"


@pytest.mark.django_db
def test_api_update_requires_choices_for_choice_field(apiclient, bs_module):
    settings = CustomFieldSettings.objects.get(module=bs_module)
    initiator = bs_module.project.organisation.initiators.first()
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=initiator)

    data = {
        "fields": [
            {"label": "District", "type": "choice", "required": False, "choices": []},
        ]
    }
    response = apiclient.put(url, data, format="json")
    assert response.status_code == 400
    assert settings.fields.count() == 0


@pytest.mark.django_db
def test_api_update_denied_for_regular_user(apiclient, bs_module, user):
    settings = CustomFieldSettings.objects.get(module=bs_module)
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=user)
    response = apiclient.put(url, {"fields": []}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_api_switching_field_to_open_removes_stored_choices(
    apiclient, bs_module, custom_field_factory, custom_field_choice_factory
):
    """Regression: open->choice->open toggles must not leave stale choices.

    Adresses the case where a field that was saved with answer options is
    switched back to an open question: the stale choices have to disappear,
    otherwise they linger in the management UI and submission form.
    """
    settings = CustomFieldSettings.objects.get(module=bs_module)
    field = custom_field_factory(settings=settings, type=CustomFieldType.CHOICE)
    choice = custom_field_choice_factory(field=field, label="Option 1")
    initiator = bs_module.project.organisation.initiators.first()
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=initiator)

    data = {
        "fields": [
            {
                "id": field.pk,
                "label": field.label,
                "type": "open",
                "required": False,
                "choices": [{"id": choice.pk, "label": "Option 1"}],
            },
        ]
    }
    response = apiclient.put(url, data, format="json")
    assert response.status_code == 200

    field.refresh_from_db()
    assert field.type == CustomFieldType.OPEN
    assert field.choices.count() == 0


@pytest.mark.django_db
def test_api_open_field_ignores_phantom_choice_from_toggle(apiclient, bs_module):
    """An open question must not persist answer options submitted alongside it.

    Reproduces the management UI toggle sequence (open -> choice -> open)
    where a local empty answer option was carried along in the payload.
    """
    settings = CustomFieldSettings.objects.get(module=bs_module)
    initiator = bs_module.project.organisation.initiators.first()
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=initiator)

    data = {
        "fields": [
            {
                "label": "Question",
                "type": "open",
                "required": False,
                "choices": [{"label": ""}],
            },
        ]
    }
    response = apiclient.put(url, data, format="json")
    assert response.status_code == 200

    open_field = settings.fields.get(type=CustomFieldType.OPEN)
    assert open_field.choices.count() == 0


@pytest.mark.django_db
def test_api_rejects_choice_field_with_only_blank_answers(apiclient, bs_module):
    settings = CustomFieldSettings.objects.get(module=bs_module)
    initiator = bs_module.project.organisation.initiators.first()
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=initiator)

    data = {
        "fields": [
            {
                "label": "District",
                "type": "choice",
                "required": False,
                "choices": [{"label": ""}, {"label": "   "}],
            },
        ]
    }
    response = apiclient.put(url, data, format="json")
    assert response.status_code == 400
    assert settings.fields.count() == 0


@pytest.mark.django_db
def test_api_update_drops_blank_answers_and_keeps_real_ones(apiclient, bs_module):
    settings = CustomFieldSettings.objects.get(module=bs_module)
    initiator = bs_module.project.organisation.initiators.first()
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=initiator)

    data = {
        "fields": [
            {
                "label": "District",
                "type": "choice",
                "required": False,
                "choices": [{"label": "North"}, {"label": ""}],
            },
        ]
    }
    response = apiclient.put(url, data, format="json")
    assert response.status_code == 200

    choice_field = settings.fields.get(type=CustomFieldType.CHOICE)
    assert list(choice_field.choices.values_list("label", flat=True)) == ["North"]
