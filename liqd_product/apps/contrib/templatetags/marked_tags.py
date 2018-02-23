from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(needs_autoescape=True)
@stringfilter
def marked_per_word(value, autoescape=True):
    result = ''
    for word in value.split():
        result += ('<div class="marked marked--multiple_lines">{}</div>'
                   .format(word))

    return mark_safe(result)
