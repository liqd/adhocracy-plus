from rest_framework import serializers

from adhocracy4.dashboard import components
from adhocracy4.dashboard import signals as a4dashboard_signals

from .models import CustomField
from .models import CustomFieldChoice
from .models import CustomFieldSettings
from .models import CustomFieldType


class CustomFieldChoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = CustomFieldChoice
        fields = ("id", "label")


class CustomFieldSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    choices = CustomFieldChoiceSerializer(many=True, required=False)

    class Meta:
        model = CustomField
        fields = ("id", "label", "type", "required", "choices")


class CustomFieldSettingsSerializer(serializers.ModelSerializer):
    fields = CustomFieldSerializer(many=True, required=False)

    class Meta:
        model = CustomFieldSettings
        fields = ("id", "fields")

    def update(self, instance, validated_data):
        fields_data = validated_data.get("fields")
        if fields_data is None:
            return instance

        keep_ids = {field["id"] for field in fields_data if field.get("id")}
        for field_id in instance.fields.values_list("id", flat=True):
            if field_id not in keep_ids:
                CustomField.objects.filter(id=field_id).delete()

        for weight, field_data in enumerate(fields_data):
            field, _ = CustomField.objects.update_or_create(
                id=field_data.get("id"),
                defaults={
                    "settings": instance,
                    "label": field_data.get("label", ""),
                    "type": field_data.get("type", CustomFieldType.OPEN),
                    "required": field_data.get("required", False),
                    "weight": weight,
                },
            )
            if field.type == CustomFieldType.CHOICE:
                choices = field_data.get("choices", [])
                self._update_choices(choices, field)

        self._send_component_updated_signal(instance)
        return instance

    def _update_choices(self, choices_data, field):
        existing_ids = set(field.choices.values_list("id", flat=True))
        keep_ids = {choice["id"] for choice in choices_data if choice.get("id")}
        CustomFieldChoice.objects.filter(
            id__in=existing_ids - keep_ids, field=field
        ).delete()

        for weight, choice_data in enumerate(choices_data):
            CustomFieldChoice.objects.update_or_create(
                id=choice_data.get("id"),
                defaults={
                    "field": field,
                    "label": choice_data.get("label", ""),
                    "weight": weight,
                },
            )

    def _send_component_updated_signal(self, settings):
        component = components.modules["custom_fields"]
        a4dashboard_signals.module_component_updated.send(
            sender=component.__class__,
            module=settings.module,
            component=component.__class__,
            user=self.context["request"].user,
        )
