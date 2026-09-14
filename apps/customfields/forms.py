from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from .models import CustomFieldAnswer
from .models import CustomFieldSettings
from .models import CustomFieldType


class CustomFieldsFormMixin(forms.Form):
    """Add the custom fields of the module settings to the form and save the
    answers on the submitted object.

    Works for all idea based modules (brainstorming, idea contest, spatial
    brainstorming and spatial idea contest). The custom field settings are
    looked up via the module that is passed to the form.
    """

    def __init__(self, *args, **kwargs):
        self.module = kwargs.get("module")
        super().__init__(*args, **kwargs)
        self.custom_field_list = []
        answers = self.get_existing_answers()
        for field in self.get_custom_fields():
            name = self.get_field_name(field)
            self.fields[name] = self.get_form_field(field)
            self.custom_field_list.append((name, field))
            if answers is not None:
                self.fields[name].initial = answers.get(field.pk, "")

    @property
    def custom_fields(self):
        """Return the bound dynamic fields in the order of the module settings."""
        return [self[name] for name, _ in self.custom_field_list]

    def get_custom_fields(self):
        if not self.module:
            return []
        settings = CustomFieldSettings.objects.filter(module=self.module).first()
        if settings:
            return settings.fields.prefetch_related("choices")
        return []

    def get_existing_answers(self):
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            content_type = ContentType.objects.get_for_model(instance.__class__)
            answers = CustomFieldAnswer.objects.filter(
                content_type=content_type, object_id=instance.pk
            )
            return {answer.field_id: answer.value for answer in answers}
        return None

    @staticmethod
    def get_field_name(field):
        return "custom_field_{}".format(field.pk)

    def get_form_field(self, field):
        if field.type == CustomFieldType.CHOICE:
            choices = [(choice.pk, choice.label) for choice in field.choices.all()]
            # Always prepend an empty placeholder option, also for required
            # questions. Without it the browser silently preselects the first
            # answer, so participants could "answer" a required question
            # without actively choosing anything.
            choices = [("", _("Please choose..."))] + choices
            return forms.ChoiceField(
                label=field.label,
                required=field.required,
                choices=choices,
                widget=forms.Select,
            )
        return forms.CharField(
            label=field.label,
            required=field.required,
            widget=forms.Textarea(attrs={"rows": 4}),
        )

    def save(self, commit=True):
        obj = super().save(commit=commit)
        if not obj.pk:
            return obj

        content_type = ContentType.objects.get_for_model(obj.__class__)
        current = {field.pk for _, field in self.custom_field_list}
        CustomFieldAnswer.objects.filter(
            content_type=content_type, object_id=obj.pk
        ).exclude(field_id__in=current).delete()

        for name, field in self.custom_field_list:
            value = self.cleaned_data.get(name)
            if value:
                CustomFieldAnswer.objects.update_or_create(
                    content_type=content_type,
                    object_id=obj.pk,
                    field=field,
                    defaults={"value": str(value)},
                )
            else:
                CustomFieldAnswer.objects.filter(
                    content_type=content_type, object_id=obj.pk, field=field
                ).delete()
        return obj
