from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from adhocracy4.models.base import TimeStampedModel
from adhocracy4.modules import models as module_models


class CustomFieldType(models.TextChoices):
    OPEN = "open", _("Open question")
    CHOICE = "choice", _("Multiple choice")


class CustomFieldSettings(module_models.AbstractSettings):
    """Module settings holding the custom fields of the idea submission form."""

    @property
    def project(self):
        return self.module.project

    def __str__(self):
        return "Custom fields for module {}".format(self.module)


class CustomField(models.Model):
    settings = models.ForeignKey(
        CustomFieldSettings, on_delete=models.CASCADE, related_name="fields"
    )
    label = models.CharField(max_length=255, verbose_name=_("Question"))
    type = models.CharField(
        max_length=20,
        choices=CustomFieldType.choices,
        verbose_name=_("Type"),
    )
    required = models.BooleanField(default=False, verbose_name=_("Required"))
    weight = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["weight"]

    def __str__(self):
        return self.label


class CustomFieldChoice(models.Model):
    field = models.ForeignKey(
        CustomField, on_delete=models.CASCADE, related_name="choices"
    )
    label = models.CharField(max_length=255, verbose_name=_("Answer"))
    weight = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["weight"]

    def __str__(self):
        return self.label


class CustomFieldAnswer(TimeStampedModel):
    """Answer to a custom field, attached to an idea or a map idea.

    Uses a generic foreign key so that all idea based modules
    (brainstorming, idea contest, spatial brainstorming and spatial idea
    contest) can store custom field answers.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    field = models.ForeignKey(
        CustomField, on_delete=models.CASCADE, related_name="answers"
    )
    value = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id", "field"],
                name="unique_answer_per_object_and_field",
            )
        ]

    def __str__(self):
        return self.value

    @property
    def display_value(self):
        if self.field.type == CustomFieldType.CHOICE and self.value:
            try:
                pk = int(self.value)
            except ValueError:
                return self.value
            # iterate the prefetched choices (when available) instead of
            # issuing a query per answer
            for choice in self.field.choices.all():
                if choice.pk == pk:
                    return choice.label
            return self.value
        return self.value
