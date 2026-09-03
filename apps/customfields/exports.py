"""Reusable export mixin adding custom field answers to idea exports.

Used by every idea based module (brainstorming, idea contest, spatial
brainstorming and spatial idea contest) so that custom fields and their
answers are included in the CSV export exactly once per module.
"""

from .models import CustomFieldSettings


class CustomFieldExportMixin:
    """Adds one export column per custom field question.

    Columns are labelled with the question text and each cell contains the
    textual answer (not an index) for the submitted object.
    """

    def get_virtual_fields(self, virtual):
        virtual = super().get_virtual_fields(virtual)
        settings = CustomFieldSettings.objects.filter(module=self.module).first()
        if settings is None:
            return virtual

        for field in settings.fields.prefetch_related("choices").all():
            name = "custom_field_{}".format(field.pk)
            virtual[name] = field.label
            setattr(
                self,
                "get_{}_data".format(name),
                self._make_custom_field_getter(field.pk),
            )
        return virtual

    def _make_custom_field_getter(self, field_id):
        def getter(item):
            for answer in item.custom_field_answers.all():
                if answer.field_id == field_id:
                    return answer.display_value
            return ""

        return getter
