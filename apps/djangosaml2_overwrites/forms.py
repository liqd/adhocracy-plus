from allauth.account.models import EmailAddress
from django import forms
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _

from apps.users.models import User


class Djangosaml2SignupForm(forms.ModelForm):
    terms_of_use = forms.BooleanField(
        label=_('Terms of use')
    )
    data_protection = forms.BooleanField(
        label=_('Data protection')
    )
    get_notifications = forms.BooleanField(
        label=pgettext_lazy(
            'diid',
            'Notifications: Yes, I would like to be notified by e-mail about '
            'the beginning and end of participation opportunities and about '
            'comments on my contributions by other users. This applies to all '
            'projects I follow.'
        ),
        required=False
    )
    get_newsletters = forms.BooleanField(
        label=pgettext_lazy(
            'diid',
            'Newsletter: Yes, I would like to receive e-mail newsletters '
            'about the projects I follow.'
        ),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'username',
            'get_notifications',
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
