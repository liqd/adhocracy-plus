from django.shortcuts import get_object_or_404
from django.utils.deprecation import MiddlewareMixin

from . import clear_organisation
from . import set_organisation
from .models import Organisation


class OrganisationMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_kwargs and 'organisation_slug' in view_kwargs:
            organisation = get_object_or_404(
                Organisation,
                slug=view_kwargs['organisation_slug'])
            request.organisation = organisation
            set_organisation(organisation)
        else:
            clear_organisation()
        return None
