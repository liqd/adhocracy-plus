from allauth.account.forms import LoginForm
from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.utils.translation import ugettext_lazy as _


class TermsSignupForm(SignupForm):
    terms_of_use = forms.BooleanField(label=_('Terms of use'), error_messages={
        'required': _('Please accept the terms of use.')
    })
    get_newsletters = forms.BooleanField(
        label=_('Send me newsletters'), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = \
            _("Your username will appear publicly next to your posts.")
        del self.fields['username'].widget.attrs['placeholder']
        del self.fields['email'].widget.attrs['placeholder']
        del self.fields['password1'].widget.attrs['placeholder']
        del self.fields['password2'].widget.attrs['placeholder']

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
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = \
            _("Your username will appear publicly next to your posts.")
        del self.fields['username'].widget.attrs['placeholder']

    def save(self, request):
        user = super(SocialTermsSignupForm, self).save(request)
        user.get_newsletters = self.cleaned_data['get_newsletters']
        user.save()
        return user


class ExtraLabelLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = _('Username/e-mail address')
        del self.fields['login'].widget.attrs['placeholder']
        del self.fields['password'].widget.attrs['placeholder']
