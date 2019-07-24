from django import template
from django.forms import CheckboxInput
from django.forms import RadioSelect

register = template.Library()


@register.filter(name='is_checkbox')
def is_checkbox(field):
    return (field.field.widget.__class__.__name__
            == CheckboxInput().__class__.__name__)


@register.filter(name='is_radiobutton')
def is_radiobutton(field):
    return (field.field.widget.__class__.__name__
            == RadioSelect().__class__.__name__)
