from django import forms

from apps.users.models import User


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'username',
            '_avatar',
            'bio',
            'homepage',
            'facebook_handle',
            'twitter_handle',
            'get_notifications',
            'get_newsletters',
            'language'
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
