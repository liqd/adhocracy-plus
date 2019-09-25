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
