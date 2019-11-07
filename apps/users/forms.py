from allauth.account.forms import SignupForm
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.utils.translation import ugettext_lazy as _


class TermsSignupForm(SignupForm):
    terms_of_use = forms.BooleanField(label=_('Terms of use'), error_messages={
        'required': _('Please accept the terms of use.')
    })
    get_newsletters = forms.BooleanField(
        label=_('Send me newsletters'), required=False)

    def save(self, request):
        user = super(TermsSignupForm, self).save(request)
        user.get_newsletters = self.cleaned_data['get_newsletters']
        user.save()
        return user


class SocialTermsSignupForm(SocialSignupForm):
    email = forms.EmailField(widget=forms.HiddenInput())
    terms_of_use = forms.BooleanField(label=_('Terms of use'), error_messages={
        'required': _('Please accept the terms of use.')
    })
    get_newsletters = forms.BooleanField(
        label=_('Send me newsletters'), required=False)

    def __init__(self, *args, **kwargs):
        initial = get_adapter().get_signup_form_initial_data(
            kwargs["sociallogin"])
        kwargs.update({'initial': initial})
        super().__init__(*args, **kwargs)

    def save(self, request):
        user = super(SocialTermsSignupForm, self).save(request)
        user.get_newsletters = self.cleaned_data['get_newsletters']
        user.save()
        return user
