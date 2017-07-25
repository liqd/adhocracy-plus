from django.shortcuts import get_object_or_404

from .models import Partner
from .urlresolvers import set_partner


class PartnerMiddleware:

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_kwargs and 'partner_slug' in view_kwargs:
            partner = get_object_or_404(Partner,
                                        slug=view_kwargs['partner_slug'])
            request.partner = partner
            set_partner(partner)
        return None
