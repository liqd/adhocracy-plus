from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from djangosaml2.utils import validate_referral_url

from apps.users.models import User

from . import forms


class Djangosaml2SignupView(LoginRequiredMixin,
                            SuccessMessageMixin,
                            generic.UpdateView):

    model = User
    template_name = 'djangosaml2_overwrites/signup.html'
    form_class = forms.Djangosaml2SignupForm
    success_message = _('Your profile was successfully updated.')

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.id)

    def get_success_url(self):
        redirect_to = self.request.POST.get("next")
        if not validate_referral_url(self.request, redirect_to):
            redirect_to = None
        return redirect_to

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        redirect_field_value = self.request.GET.get("next")
        site = get_current_site(self.request)
        ret.update({"site": site,
                    "redirect_field_name": "next",
                    "redirect_field_value": redirect_field_value})
        return ret
