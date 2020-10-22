from allauth.account.models import EmailAddress
from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.users.models import User


class Djangosaml2SignupForm(forms.ModelForm):
    terms_of_use = forms.BooleanField(
        label=_('Terms of use')
    )
    get_newsletters = forms.BooleanField(
        label=_('I would like to receive further information'),
        help_text=_('Projects you are following can send you '
                    'additional information via email.'),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'username',
            'get_newsletters'
        ]

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username__iexact=username)
            if user != self.instance:
                raise forms.ValidationError(
                    User._meta.get_field('username').error_messages['unique'])
        except User.DoesNotExist:
            pass
        return username

    def save(self):
        email_address = EmailAddress.objects.get(user=self.instance,
                                                 email=self.instance.email)
        email_address.verified = True
        email_address.save()
        super().save()
