from allauth.socialaccount.adapter import get_adapter
from allauth.utils import email_address_exists
from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class TermsSignupForm(auth_forms.UserCreationForm):
    terms_of_use = forms.BooleanField(label=_('Terms of use'), error_messages={
        'required': _('Please accept the terms of use.')
    })

    def signup(self, request, user):
        user.signup(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
        )

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2',
                  'terms_of_use', 'get_newsletters')

# Tried to add form as described in allauth documentation:
# https://django-allauth.readthedocs.io/en/latest/forms.html#socialaccount-forms
# ran into the following error:
# https://stackoverflow.com/questions/57254251/custom-form-with-socialaccount-in-django-allauth
# added this solution, maybe not the best


class SignupForm(forms.Form):
    terms_of_use = forms.BooleanField(label=_('Terms of use'), error_messages={
        'required': _('Please accept the terms of use.')
    })
    get_newsletters = forms.BooleanField(
        label=_('Send me newsletters'), required=False)
    email = forms.EmailField(widget=forms.HiddenInput())
    username = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.sociallogin = kwargs.pop('sociallogin')
        initial = get_adapter().get_signup_form_initial_data(
            self.sociallogin)
        kwargs.update({
            'initial': initial})
        super().__init__(*args, **kwargs)

    def save(self, request):
        adapter = get_adapter(request)
        user = adapter.save_user(request, self.sociallogin, form=self)
        user.get_newsletters = self.cleaned_data['get_newsletters']
        user.save()
        user.signup(
            user.username,
            user.email
        )
        return user

    def clean(self):
        email = self.cleaned_data['email']
        if email_address_exists(email):
            raise forms.ValidationError(
                get_adapter().error_messages['email_taken']
                % self.sociallogin.account.get_provider().name)
        return super().clean()
