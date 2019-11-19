from allauth.account.forms import LoginForm
from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _


class TermsSignupForm(SignupForm):
    terms_of_use = forms.BooleanField(
        label=_('Terms of use')
    )
    get_newsletters = forms.BooleanField(
        label=_('Info Mails'),
        help_text=_('Projects I follow are allowed to send me '
                    'information mails.'),
        required=False
    )

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
        user.language = get_language()
        user.save()
        return user


class SocialTermsSignupForm(SocialSignupForm):
    terms_of_use = forms.BooleanField(
        label=_('Terms of use')
    )
    get_newsletters = forms.BooleanField(
        label=_('Info Mails'),
        help_text=_('Projects I follow are allowed to send me '
                    'information mails.'),
        required=False
    )
    email = forms.EmailField(
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = \
            _("Your username will appear publicly next to your posts.")
        del self.fields['username'].widget.attrs['placeholder']

    def save(self, request):
        user = super(SocialTermsSignupForm, self).save(request)
        user.get_newsletters = self.cleaned_data['get_newsletters']
        user.language = get_language()
        user.save()
        return user


class ExtraLabelLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = _('Username/e-mail')
        del self.fields['login'].widget.attrs['placeholder']
        del self.fields['password'].widget.attrs['placeholder']
