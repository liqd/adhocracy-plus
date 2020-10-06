import parler
from ckeditor_uploader import widgets
from ckeditor_uploader.fields import RichTextUploadingFormField
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from adhocracy4 import transforms
from apps.cms.settings import helpers
from apps.organisations.models import OrganisationTranslation

from .models import Organisation

IMPRINT_HELP = _('Here you can find an example of an {}imprint{}.')
TERMS_OF_USE_HELP = _('Here you can find an example of {}terms of use{}.')
DATA_PROTECTION_HELP = _('Here you can find an example of a '
                         '{}data protection policy{}.')
NETIQUETTE_HELP = _('Here you can find an example of a {}netiquette{}.')

_external_plugin_resources = [(
    'collapsibleItem',
    '/static/ckeditor_collapsible/',
    'plugin.js',
)]


class OrganisationForm(forms.ModelForm):

    translated_fields = [
        ('description', forms.CharField, {
            'label': OrganisationTranslation._meta.get_field(
                'description').verbose_name,
            'help_text': OrganisationTranslation._meta.get_field(
                'description').help_text,
            'max_length': OrganisationTranslation._meta.get_field(
                'description').max_length,
            'widget': forms.Textarea({'rows': 4}),
        }),
        ('slogan', forms.CharField, {
            'label': OrganisationTranslation._meta.get_field(
                'slogan').verbose_name,
            'help_text': OrganisationTranslation._meta.get_field(
                'slogan').help_text,
            'max_length': OrganisationTranslation._meta.get_field(
                'slogan').max_length,
            'widget': forms.Textarea({'rows': 2}),
        }),
        ('information', RichTextUploadingFormField, {
            'config_name': 'collapsible-image-editor',
            'label': OrganisationTranslation._meta.get_field(
                'information').verbose_name,
            'help_text': OrganisationTranslation._meta.get_field(
                'information').help_text,
            'external_plugin_resources': _external_plugin_resources,
            'extra_plugins': ['collapsibleItem'],
            'widget': widgets.CKEditorUploadingWidget(
                external_plugin_resources=_external_plugin_resources,
                extra_plugins=['collapsibleItem'],
                config_name='collapsible-image-editor')
        })
    ]
    languages = [lang_code for lang_code, lang in settings.LANGUAGES]

    class Meta:
        model = Organisation
        fields = ['title', 'logo', 'image', 'image_copyright', 'url',
                  'twitter_handle', 'facebook_handle', 'instagram_handle',
                  'language']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'required': 'true'})
        for lang_code in self.languages:
            for name, field_cls, kwargs in self.translated_fields:
                self.instance.set_current_language(lang_code)
                field = field_cls(**kwargs)
                identifier = self._get_identifier(
                    lang_code, name)
                field.required = False

                try:
                    translation = self.instance.get_translation(lang_code)
                    initial = getattr(translation, name)
                except parler.models.TranslationDoesNotExist:
                    initial = ''

                field.initial = initial

                self.fields[identifier] = field

    def _get_identifier(self, language, fieldname):
        return '{}__{}'.format(language, fieldname)

    def translated(self):
        from itertools import groupby
        fields = [(field.html_name.split('__')[0], field) for field in self
                  if '__' in field.html_name]
        groups = groupby(fields, lambda x: x[0])
        values = [(lang, list(map(lambda x: x[1], group)))
                  for lang, group in groups]
        return values

    def untranslated(self):
        return [field for field in self if '__' not in field.html_name]

    def prefilled_languages(self):
        languages = [lang for lang in self.languages
                     if lang in self.data
                     or self.instance.has_translation(lang)]
        return languages

    def get_initial_active_tab(self):
        active_languages = self.prefilled_languages()
        if len(active_languages) > 0:
            return active_languages[0]
        else:
            return 'de'

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit is True:
            for lang_code in self.languages:
                if lang_code in self.data:
                    instance.set_current_language(lang_code)
                    for fieldname, _cls, _kwargs in self.translated_fields:
                        identifier = '{}__{}'.format(lang_code, fieldname)
                        if fieldname == 'information':
                            field_data = transforms.clean_html_field(
                                self.cleaned_data.get(identifier),
                                'collapsible-image-editor')
                        else:
                            field_data = self.cleaned_data.get(identifier)
                        setattr(instance, fieldname,
                                field_data)
                    instance.save()
                elif instance.has_translation(lang_code):
                    instance.delete_translation(lang_code)
        return instance


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
