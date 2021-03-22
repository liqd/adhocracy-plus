import logging

import xmltodict
from allauth.account.forms import LoginForm
from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.conf import settings
from django.contrib.auth import forms as auth_forms
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from zeep import Client

from apps.captcha.fields import CaptcheckCaptchaField
from apps.organisations.models import Member
from apps.organisations.models import Organisation
from apps.users.models import User

logger = logging.getLogger(__name__)


class DefaultLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = _('Username/e-mail')
        del self.fields['login'].widget.attrs['placeholder']
        del self.fields['password'].widget.attrs['placeholder']
        self.fields['login'].widget.attrs['autocomplete'] = 'username'
        self.fields['password'].widget.attrs['autocomplete'] = \
            'current-password'


class DefaultSignupForm(SignupForm):
    terms_of_use = forms.BooleanField(
        label=_('Terms of use')
    )
    get_newsletters = forms.BooleanField(
        label=_('I would like to receive further information'),
        help_text=_('Projects you are following can send you '
                    'additional information via email.'),
        required=False
    )
    captcha = CaptcheckCaptchaField(label=_('I am not a robot'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = \
            _("Your username will appear publicly next to your posts.")
        self.fields['email'].widget.attrs['autofocus'] = True
        del self.fields['username'].widget.attrs['placeholder']
        del self.fields['email'].widget.attrs['placeholder']
        del self.fields['password1'].widget.attrs['placeholder']
        del self.fields['password2'].widget.attrs['placeholder']
        self.fields['email'].widget.attrs['autocomplete'] = 'username'
        self.fields['password1'].widget.attrs['autocomplete'] = 'new-password'
        self.fields['password2'].widget.attrs['autocomplete'] = 'new-password'

    def save(self, request):
        user = super().save(request)
        user.get_newsletters = self.cleaned_data['get_newsletters']
        user.language = get_language()
        user.save()
        return user


class IgbceSignupForm(DefaultSignupForm):
    member_number = forms.IntegerField(
        label=_('Membership number of IG BCE'),
        help_text=_('The membership number consists of a seven-digit number '
                    'and can be found on the membership card.'),
        max_value=99999999999999999999,
        min_value=0
    )
    birth_date = forms.DateField(
        label=_('Date of birth'),
        help_text=_('Please also enter your date of birth in the format '
                    'MM/DD/YYYY for authentication. Only members of the '
                    'IG BCE can participate.')
    )
    terms_of_use_extra = forms.BooleanField(
        label=_('I confirm that I have read and accepted the '
                '<a href="/info/ig-bce-datenschutz/" '
                'target="_blank">data protection policy</a> of IG '
                'BCE.')
    )

    def validateMemberNumberAndDate(self, member_number, birth_date):

        if (not hasattr(settings, 'IGBCE_NAV_URL') or
                not hasattr(settings, 'IGBCE_NAV_SECURITYID')):
            raise forms.ValidationError(
                _('Something is wrong with the setup - please try again later')
            )

        if Member.objects.filter(member_number=member_number).exists():
            raise forms.ValidationError(
                _('There is already a participant with this membership '
                  'number. Please check your entry. If this is your '
                  'membership number, please send an email to '
                  '"zukunftsgewerkschaft@igbce.de".')
            )

        result = False
        try:
            client = Client('{}'.format(settings.IGBCE_NAV_URL))
            parameters = "{};{}".format(member_number,
                                        birth_date.strftime("%d.%m.%Y"))
            connection_parameters = \
                "ObjectID:0;SecurityID:{};SetSize:0;UnitopProxyVersion:2.0" \
                .format(settings.IGBCE_NAV_SECURITYID)

            response = client.service.SendRequest(
                functionName="CALCONNECT_MemberNoBirthDate",
                functionParameters=parameters,
                filters="",
                connectionParameters=connection_parameters
            )

            result_str = (xmltodict.parse(response)['Response']['ResponseData']
                          ['Object']['CalConnectorResult'])

            if result_str == 'true':
                result = True

        except BaseException:
            logger.exception("IGBCE API error")
            raise forms.ValidationError(
                _('Something is wrong with the setup - please try again later')
            )

        if not result:
            raise forms.ValidationError(
                _('Unfortunately, the member number and / or date of birth '
                  'could not be linked to an active member account. Please '
                  'check your input and try again. If you still have '
                  'problems, please contact "zukunftsgewerkschaft@igbce.de".')
            )

    def clean(self):
        super().clean()

        if any(self.errors):
            return self.errors

        member_number = self.cleaned_data.get('member_number')
        birth_date = self.cleaned_data.get('birth_date')

        self.validateMemberNumberAndDate(member_number, birth_date)

    def save(self, request):

        user = super().save(request)
        if hasattr(settings, 'SITE_ORGANISATION_SLUG'):
            organisation = Organisation.objects.get(
                slug=settings.SITE_ORGANISATION_SLUG
            )
            additional_info = {
                'birth_date': self.cleaned_data['birth_date']
            }
            member = Member(
                member=user,
                member_number=self.cleaned_data['member_number'],
                organisation=organisation,
                additional_info=additional_info
            )
            member.save()
        return user


class SocialTermsSignupForm(SocialSignupForm):
    terms_of_use = forms.BooleanField(
        label=_('Terms of use')
    )
    get_newsletters = forms.BooleanField(
        label=_('I would like to receive further information'),
        help_text=_('Projects you are following can send you '
                    'additional information via email.'),
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
        user = super().save(request)
        user.get_newsletters = self.cleaned_data['get_newsletters']
        user.language = get_language()
        user.save()
        return user


class ChangeUserAdminForm(auth_forms.UserChangeForm):

    def clean_username(self):

        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username__iexact=username)
            if user != self.instance:
                raise forms.ValidationError(
                    User._meta.get_field('username').error_messages['unique'])
        except User.DoesNotExist:
            pass

        try:
            user = User.objects.get(email__iexact=username)
            if user != self.instance:
                raise forms.ValidationError(User._meta.get_field('username').
                                            error_messages['used_as_email'])
        except User.DoesNotExist:
            pass

        return username


class AddUserAdminForm(auth_forms.UserCreationForm):

    def clean_username(self):

        username = self.cleaned_data['username']
        user = User.objects.filter(username__iexact=username)
        if user.exists():
            raise forms.ValidationError(
                User._meta.get_field('username').error_messages['unique'])
        else:
            user = User.objects.filter(email__iexact=username)
            if user.exists():
                raise forms.ValidationError(User._meta.get_field('username').
                                            error_messages['used_as_email'])
        return username
