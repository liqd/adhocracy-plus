from django import forms

from .models import Partner


class PartnerForm(forms.ModelForm):

    class Meta:
        model = Partner
        fields = ['title', 'logo', 'description', 'slogan', 'image',
                  'information', 'imprint']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget = forms.Textarea({'rows': 4})
        self.fields['slogan'].widget = forms.Textarea({'rows': 2})
