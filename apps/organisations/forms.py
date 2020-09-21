from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.cms.settings import helpers

from .models import Organisation

IMPRINT_HELP = _('Here you can find an example of an {}imprint{}.')
TERMS_OF_USE_HELP = _('Here you can find an example of {}terms of use{}.')
DATA_PROTECTION_HELP = _('Here you can find an example of a '
                         '{}data protection policy{}.')
NETIQUETTE_HELP = _('Here you can find an example of a {}netiquette{}.')


class OrganisationForm(forms.ModelForm):

    class Meta:
        model = Organisation
        fields = ['title', 'slogan_untranslated', 'description_untranslated',
                  'information_untranslated',
                  'logo', 'image', 'image_copyright', 'url',
                  'twitter_handle', 'facebook_handle', 'instagram_handle']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'required': 'true'})
        self.fields['description'].widget = forms.Textarea({'rows': 4})
        self.fields['slogan'].widget = forms.Textarea({'rows': 2})


class OrganisationLegalInformationForm(forms.ModelForm):

    class Meta:
        model = Organisation
        fields = ['imprint', 'terms_of_use', 'data_protection',
                  'netiquette']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imprint'].help_text = helpers.add_link_to_helptext(
            self.fields['imprint'].help_text, "imprint",
            IMPRINT_HELP)
        self.fields['terms_of_use'].help_text = helpers.add_link_to_helptext(
            self.fields['terms_of_use'].help_text, "terms_of_use",
            TERMS_OF_USE_HELP)
        self.fields['data_protection'].help_text \
            = helpers.add_link_to_helptext(
                self.fields['data_protection'].help_text,
                "data_protection_policy",
                DATA_PROTECTION_HELP)
        self.fields['netiquette'].help_text = helpers.add_link_to_helptext(
            self.fields['netiquette'].help_text, "netiquette",
            NETIQUETTE_HELP)
