import xmltodict
from allauth.account.forms import LoginForm
from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from zeep import Client

from apps.captcha.fields import CaptcheckCaptchaField
from apps.captcha.mixins import CaptcheckCaptchaFormMixin
from apps.organisations.models import Member
from apps.organisations.models import Organisation


class DefaultLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = _('Username/e-mail')
        del self.fields['login'].widget.attrs['placeholder']
        del self.fields['password'].widget.attrs['placeholder']


class DefaultSignupForm(CaptcheckCaptchaFormMixin, SignupForm):
    terms_of_use = forms.BooleanField(
        label=_('Terms of use')
    )
    get_newsletters = forms.BooleanField(
        label=_('Info Mails'),
        help_text=_('Projects I follow are allowed to send me '
                    'information mails.'),
        required=False
    )
    captcha = CaptcheckCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = \
            _("Your username will appear publicly next to your posts.")
        del self.fields['username'].widget.attrs['autofocus']
        self.fields['email'].widget.attrs['autofocus'] = True
        del self.fields['username'].widget.attrs['placeholder']
        del self.fields['email'].widget.attrs['placeholder']
        del self.fields['password1'].widget.attrs['placeholder']
        del self.fields['password2'].widget.attrs['placeholder']

    def save(self, request):
        user = super().save(request)
        user.get_newsletters = self.cleaned_data['get_newsletters']
        user.language = get_language()
        user.save()
        return user


class IgbceSignupForm(DefaultSignupForm):
    member_number = forms.IntegerField(
        label=_('IG-BCE member number'),
        help_text=_('Some helptext.'),
        max_value=99999999999999999999,
        min_value=0
    )
    birth_date = forms.DateField(
        label=_('Birth date'),
        help_text=_('Some helptext.')
    )

    def validateMemberNumberAndDate(self, member_number, birth_date):

        if (not hasattr(settings, 'IGBCE_NAV_URL') or
                not hasattr(settings, 'IGBCE_NAV_SECURITYID')):
            raise forms.ValidationError(
                "Something is wrong with the setup - please try again later"
            )

        if Member.objects.filter(member_number=member_number).exists():
            raise forms.ValidationError(
                "A member with that number already exists."
            )

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
        result = False
        if result_str == 'true':
            result = True

        if not result:
            raise forms.ValidationError(
                "Your credentials couldn't be connected to an IGBCE member. "
                "Please check your member number and birthdate again."
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
        user = super().save(request)
        user.get_newsletters = self.cleaned_data['get_newsletters']
        user.language = get_language()
        user.save()
        return user
