import pytest
from django.urls import reverse

from apps.customfields.models import CustomField
from apps.customfields.models import CustomFieldSettings
from apps.customfields.models import CustomFieldType


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
def test_api_update_denied_for_regular_user(apiclient, bs_module, user):
    settings = CustomFieldSettings.objects.get(module=bs_module)
    url = reverse("custom-fields-detail", kwargs={"pk": settings.pk})
    apiclient.force_authenticate(user=user)
    response = apiclient.put(url, {"fields": []}, format="json")
    assert response.status_code == 403
