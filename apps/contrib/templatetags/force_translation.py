import re

from django.template import Library
from django.template import Node
from django.template import TemplateSyntaxError
from django.utils import translation

register = Library()


class ForceTransNode(Node):
    def __init__(self, nodelist, language_name):
        self.nodelist = nodelist
        self.language_name = language_name

    def render(self, context):
        with translation.override(self.language_name):
            return self.nodelist.render(context)


def force_translation(parser, token):
    """
    Parse force_translation template tag.

    .. code:: django
      {% force_translation 'en' %}
          {{ _('Will always be english') }}
      {% endforce_translation %}
    """
    try:
        nodelist = parser.parse(('endforce_translation',))
        parser.delete_first_token()
        tag_name, language_name = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError(
            '{} tag requires arguments'.format(token.contents.split()[0])
        )
    match = re.match(r'["\']([a-z]{2}(:?_[A-Z]{2}})?)["\']', language_name)
    if not match:
        raise TemplateSyntaxError(
            '{} locale should be in ll[_LL] format and in quotes'.format(
                tag_name
            )
        )
    return ForceTransNode(nodelist, match.group(1))


register.tag('force_translation', force_translation)
