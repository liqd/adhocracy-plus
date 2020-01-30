from django import forms

from .models import Organisation


class OrganisationForm(forms.ModelForm):

    class Meta:
        model = Organisation
        fields = ['title', 'logo', 'description', 'slogan', 'image',
                  'image_copyright', 'information', 'imprint', 'url',
                  'twitter_handle', 'facebook_handle', 'instagram_handle']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget = forms.Textarea({'rows': 4})
        self.fields['slogan'].widget = forms.Textarea({'rows': 2})
