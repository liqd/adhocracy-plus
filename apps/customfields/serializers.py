from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from adhocracy4.dashboard import components
from adhocracy4.dashboard import signals as a4dashboard_signals

from .models import CustomField
from .models import CustomFieldChoice
from .models import CustomFieldSettings
from .models import CustomFieldType


class CustomFieldChoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    label = serializers.CharField(required=True, allow_blank=True, max_length=255)

    class Meta:
        model = CustomFieldChoice
        fields = ("id", "label")


class CustomFieldSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    choices = CustomFieldChoiceSerializer(many=True, required=False)

    class Meta:
        model = CustomField
        fields = ("id", "label", "type", "required", "choices")

    def validate(self, attrs):
        if attrs.get("type") != CustomFieldType.CHOICE:
            return attrs

        choices = attrs.get("choices") or []
        non_blank_choices = [
            choice for choice in choices if (choice.get("label") or "").strip()
        ]
        if not non_blank_choices:
            raise serializers.ValidationError(
                {"choices": _("A multiple choice question needs at least one answer.")}
            )
        return attrs


class CustomFieldSettingsSerializer(serializers.ModelSerializer):
    fields = CustomFieldSerializer(many=True, required=False)

    class Meta:
        model = CustomFieldSettings
        fields = ("id", "fields")

    def update(self, instance, validated_data):
        with transaction.atomic():
            fields_data = validated_data.get("fields")
            if fields_data is None:
                return instance

            allowed_ids = set(instance.fields.values_list("id", flat=True))
            submitted_ids = {field["id"] for field in fields_data if field.get("id")}
            if not submitted_ids <= allowed_ids:
                raise serializers.ValidationError(
                    {"fields": _("Submitted field ids do not belong to this module.")}
                )

            for field_id in allowed_ids - submitted_ids:
                CustomField.objects.filter(id=field_id).delete()

            for weight, field_data in enumerate(fields_data):
                field, created = CustomField.objects.update_or_create(
                    id=field_data.get("id"),
                    settings=instance,
                    defaults={
                        "label": field_data.get("label", ""),
                        "type": field_data.get("type", CustomFieldType.OPEN),
                        "required": field_data.get("required", False),
                        "weight": weight,
                    },
                )
                if field.type == CustomFieldType.CHOICE:
                    choices = field_data.get("choices", [])
                    self._update_choices(choices, field)
                else:
                    # Open questions must not keep stale answer options. They
                    # would otherwise linger after switching a question type
                    # and leak into the submission form or later saves.
                    field.choices.all().delete()

        self._send_component_updated_signal(instance)
        return instance

    def _update_choices(self, choices_data, field):
        # Drop blank answer options (e.g. auto-seeded placeholders) instead of
        # persisting empty selectable answers.
        choices_data = [
            choice for choice in choices_data if (choice.get("label") or "").strip()
        ]

        allowed_ids = set(field.choices.values_list("id", flat=True))
        submitted_ids = {choice["id"] for choice in choices_data if choice.get("id")}
        if not submitted_ids <= allowed_ids:
            raise serializers.ValidationError(
                {"choices": _("Submitted choice ids do not belong to this field.")}
            )

        for choice_id in allowed_ids - submitted_ids:
            CustomFieldChoice.objects.filter(id=choice_id, field=field).delete()

        for weight, choice_data in enumerate(choices_data):
            CustomFieldChoice.objects.update_or_create(
                id=choice_data.get("id"),
                field=field,
                defaults={
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
