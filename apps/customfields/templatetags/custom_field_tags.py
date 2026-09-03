from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.filter
def custom_field_settings(item):
    """Return the custom field settings of the item's module or ``None``.

    Uses the reverse one-to-one relation so the prefetched value is served
    from the query cache where available.
    """
    try:
        return item.module.customfieldsettings_settings
    except ObjectDoesNotExist:
        return None


@register.filter
def answer_for(item, field):
    """Return the display value of the item's answer for a field.

    Returns ``None`` when the item has no answer for the field, so templates
    can render a placeholder for unanswered questions.
    """
    for answer in item.custom_field_answers.all():
        if answer.field_id == field.id:
            return answer.display_value
    return None
