from django import forms

from liqd_product.apps.users.models import User


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'username',
            'avatar',
            'bio',
            'homepage',
            'facebook_handle',
            'twitter_handle',
            'get_notifications'
        ]
