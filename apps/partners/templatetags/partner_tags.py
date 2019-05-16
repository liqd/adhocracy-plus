from django import template

from .. import get_partner
from .. import partner_context

register = template.Library()


class WithPartnerNode(template.Node):
    def __init__(self, nodelist, partner):
        self.nodelist = nodelist
        self.partner = template.Variable(partner)

    def render(self, context):
        actual_partner = self.partner.resolve(context)
        with partner_context(actual_partner):
            output = self.nodelist.render(context)
        return output


@register.tag
def withpartner(parser, token):
    tag_name, partner = token.split_contents()
    nodelist = parser.parse(('endwithpartner',))
    parser.delete_first_token()
    return WithPartnerNode(nodelist, partner)


@register.simple_tag
def get_current_partner():
    return get_partner()
