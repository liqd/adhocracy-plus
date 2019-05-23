from django.shortcuts import get_object_or_404
from django.utils.deprecation import MiddlewareMixin

from . import clear_partner
from . import set_partner
from .models import Partner


class PartnerMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_kwargs and 'partner_slug' in view_kwargs:
            partner = get_object_or_404(Partner,
                                        slug=view_kwargs['partner_slug'])
            request.partner = partner
            set_partner(partner)
        else:
            clear_partner()
        return None
