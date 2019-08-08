from django import template
from django.urls import resolve

from apps.organisations.models import Organisation

from .. import organisation_context

register = template.Library()


class WithOrganisationNode(template.Node):
    def __init__(self, nodelist, organisation):
        self.nodelist = nodelist
        self.organisation = template.Variable(organisation)

    def render(self, context):
        actual_organisation = self.organisation.resolve(context)
        with organisation_context(actual_organisation):
            output = self.nodelist.render(context)
        return output


@register.tag
def withorganisation(parser, token):
    tag_name, organisation = token.split_contents()
    nodelist = parser.parse(('endwithorganisation',))
    parser.delete_first_token()
    return WithOrganisationNode(nodelist, organisation)


@register.simple_tag(takes_context=True)
def get_current_organisation(context):
    request = context.request
    resolver = resolve(request.path_info)
    if resolver.kwargs and 'organisation_slug' in resolver.kwargs:
        return Organisation.objects.get(
            slug=resolver.kwargs['organisation_slug'])
