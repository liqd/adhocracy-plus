from django import forms

from .models import CustomFieldAnswer
from .models import CustomFieldType


class CustomFieldsFormMixin(forms.Form):
    """Add the custom fields of the module settings to the form and save the
    answers on the submitted object."""

    def __init__(self, *args, **kwargs):
        self.settings_instance = kwargs.pop("settings_instance", None)
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
        if self.settings_instance:
            return self.settings_instance.fields.all()
        return []

    def get_existing_answers(self):
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            answers = CustomFieldAnswer.objects.filter(idea=instance)
            return {answer.field_id: answer.value for answer in answers}
        return None

    @staticmethod
    def get_field_name(field):
        return "custom_field_{}".format(field.pk)

    def get_form_field(self, field):
        if field.type == CustomFieldType.CHOICE:
            choices = [(choice.pk, choice.label) for choice in field.choices.all()]
            if not field.required:
                choices = [("", "---------")] + choices
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
        idea = super().save(commit=commit)
        if self.settings_instance and self.custom_field_list and idea.pk:
            CustomFieldAnswer.objects.filter(idea=idea).delete()
            for name, field in self.custom_field_list:
                value = self.cleaned_data.get(name)
                if value:
                    CustomFieldAnswer.objects.create(
                        idea=idea, field=field, value=str(value)
                    )
        return idea
