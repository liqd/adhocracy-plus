from django import template
from django.urls import Resolver404
from django.urls import resolve

from apps.organisations.models import Organisation

register = template.Library()


@register.simple_tag(takes_context=True)
def get_current_organisation(context):
    try:
        request = context.request
        resolver = resolve(request.path_info)
        if resolver.kwargs and 'organisation_slug' in resolver.kwargs:
            return Organisation.objects.get(
                slug=resolver.kwargs['organisation_slug'])
    except (Resolver404, Organisation.DoesNotExist, AttributeError):
        pass
