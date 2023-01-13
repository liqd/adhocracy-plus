import parler
from ckeditor_uploader import widgets
from ckeditor_uploader.fields import RichTextUploadingFormField
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from adhocracy4 import transforms
from apps.cms.settings import helpers
from apps.contrib.widgets import ImageInputWidgetSimple
from apps.organisations.models import OrganisationTranslation
from apps.projects.models import Project

from .models import Organisation

IMPRINT_HELP = _("Here you can find an example of an {}imprint{}.")
TERMS_OF_USE_HELP = _("Here you can find an example of {}terms of use{}.")
DATA_PROTECTION_HELP = _(
    "Here you can find an example of a " "{}data protection policy{}."
)
NETIQUETTE_HELP = _("Here you can find an example of a {}netiquette{}.")

_external_plugin_resources = [
    (
        "collapsibleItem",
        "/static/ckeditor_collapsible/",
        "plugin.js",
    )
]


SOCIAL_MEDIA_CHOICES = [
    (1, _("Instagram Post 1080x1080")),
    (2, _("Instagram Story 1080x1920")),
    (3, _("Linkedin 1104x736")),
    (4, _("Twitter 1200x675")),
]

SOCIAL_MEDIA_SIZES = {
    1: {
        "title_max_length": 30,
        "title_size": 72,
        "title_y": 810,
        "description_max_length": 45,
        "description_size": 48,
        "description_y": 902,
        "img_min_width": 1080,
        "img_min_height": 760,
        "aplus_logo_width": 228,
        "aplus_logo_height": 56,
        "aplus_logo_y": 970,
        "org_logo_y": 80,
        "overall_height": 1080,
    },
    2: {
        "title_max_length": 30,
        "title_size": 72,
        "title_y": 1462,
        "description_max_length": 45,
        "description_size": 48,
        "description_y": 1554,
        "img_min_width": 1080,
        "img_min_height": 1278,
        "aplus_logo_width": 360,
        "aplus_logo_height": 88,
        "aplus_logo_y": 1654,
        "org_logo_y": 1054,
        "overall_height": 1920,
    },
    3: {
        "title_max_length": 30,
        "title_size": 48,
        "title_y": 524,
        "description_max_length": 45,
        "description_size": 40,
        "description_y": 588,
        "img_min_width": 1104,
        "img_min_height": 482,
        "aplus_logo_width": 196,
        "aplus_logo_height": 48,
        "aplus_logo_y": 634,
        "org_logo_y": 80,
        "overall_height": 736,
    },
    4: {
        "title_max_length": 30,
        "title_size": 56,
        "title_y": 480,
        "description_max_length": 45,
        "description_size": 40,
        "description_y": 548,
        "img_min_width": 1200,
        "img_min_height": 448,
        "aplus_logo_width": 196,
        "aplus_logo_height": 48,
        "aplus_logo_y": 602,
        "org_logo_y": 80,
        "overall_height": 675,
    },
}


class OrganisationForm(forms.ModelForm):

    translated_fields = [
        (
            "description",
            forms.CharField,
            {
                "label": OrganisationTranslation._meta.get_field(
                    "description"
                ).verbose_name,
                "help_text": OrganisationTranslation._meta.get_field(
                    "description"
                ).help_text,
                "max_length": OrganisationTranslation._meta.get_field(
                    "description"
                ).max_length,
                "widget": forms.Textarea({"rows": 4}),
            },
        ),
        (
            "slogan",
            forms.CharField,
            {
                "label": OrganisationTranslation._meta.get_field("slogan").verbose_name,
                "help_text": OrganisationTranslation._meta.get_field(
                    "slogan"
                ).help_text,
                "max_length": OrganisationTranslation._meta.get_field(
                    "slogan"
                ).max_length,
                "widget": forms.Textarea({"rows": 2}),
            },
        ),
        (
            "information",
            RichTextUploadingFormField,
            {
                "config_name": "collapsible-image-editor",
                "label": OrganisationTranslation._meta.get_field(
                    "information"
                ).verbose_name,
                "help_text": OrganisationTranslation._meta.get_field(
                    "information"
                ).help_text,
                "external_plugin_resources": _external_plugin_resources,
                "extra_plugins": ["collapsibleItem"],
                "widget": widgets.CKEditorUploadingWidget(
                    external_plugin_resources=_external_plugin_resources,
                    extra_plugins=["collapsibleItem"],
                    config_name="collapsible-image-editor",
                ),
            },
        ),
    ]
    languages = [lang_code for lang_code, lang in settings.LANGUAGES]

    class Meta:
        model = Organisation
        fields = [
            "title",
            "logo",
            "image",
            "image_copyright",
            "url",
            "twitter_handle",
            "facebook_handle",
            "instagram_handle",
            "language",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"required": "true"})
        for lang_code in self.languages:
            for name, field_cls, kwargs in self.translated_fields:
                self.instance.set_current_language(lang_code)
                field = field_cls(**kwargs)
                identifier = self._get_identifier(lang_code, name)
                field.required = False

                try:
                    translation = self.instance.get_translation(lang_code)
                    initial = getattr(translation, name)
                except parler.models.TranslationDoesNotExist:
                    initial = ""

                field.initial = initial

                self.fields[identifier] = field

    def _get_identifier(self, language, fieldname):
        return "{}__{}".format(language, fieldname)

    def translated(self):
        from itertools import groupby

        fields = [
            (field.html_name.split("__")[0], field)
            for field in self
            if "__" in field.html_name
        ]
        groups = groupby(fields, lambda x: x[0])
        values = [(lang, list(map(lambda x: x[1], group))) for lang, group in groups]
        return values

    def untranslated(self):
        return [field for field in self if "__" not in field.html_name]

    def prefilled_languages(self):
        languages = [
            lang
            for lang in self.languages
            if lang in self.data or self.instance.has_translation(lang)
        ]
        return languages

    def get_initial_active_tab(self):
        active_languages = self.prefilled_languages()
        if len(active_languages) > 0:
            return active_languages[0]
        else:
            return "de"

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit is True:
            for lang_code in self.languages:
                if lang_code in self.data:
                    instance.set_current_language(lang_code)
                    for fieldname, _cls, _kwargs in self.translated_fields:
                        identifier = "{}__{}".format(lang_code, fieldname)
                        if fieldname == "information":
                            field_data = transforms.clean_html_field(
                                self.cleaned_data.get(identifier),
                                "collapsible-image-editor",
                            )
                        else:
                            field_data = self.cleaned_data.get(identifier)
                        setattr(instance, fieldname, field_data)
                    instance.save()
                elif instance.has_translation(lang_code):
                    instance.delete_translation(lang_code)
        return instance


class OrganisationLegalInformationForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = ["imprint", "terms_of_use", "data_protection", "netiquette"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["imprint"].help_text = helpers.add_link_to_helptext(
            self.fields["imprint"].help_text, "imprint", IMPRINT_HELP
        )
        self.fields["terms_of_use"].help_text = helpers.add_link_to_helptext(
            self.fields["terms_of_use"].help_text, "terms_of_use", TERMS_OF_USE_HELP
        )
        self.fields["data_protection"].help_text = helpers.add_link_to_helptext(
            self.fields["data_protection"].help_text,
            "data_protection_policy",
            DATA_PROTECTION_HELP,
        )
        self.fields["netiquette"].help_text = helpers.add_link_to_helptext(
            self.fields["netiquette"].help_text, "netiquette", NETIQUETTE_HELP
        )


class CommunicationProjectChoiceForm(forms.Form):
    def __init__(self, organisation=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        project_qs = Project.objects
        if organisation:
            project_qs = Project.objects.filter(organisation=organisation.id)

        self.fields["format"] = forms.ChoiceField(
            label=_("Social Media"),
            choices=SOCIAL_MEDIA_CHOICES,
            required=True,
            help_text=_(
                "Here you can create sharepics for social media that "
                "will help you get publicity for your project. You "
                "can choose between different formats."
            ),
        )

        self.fields["project"] = forms.ModelChoiceField(
            label=_("Select Project"),
            queryset=project_qs,
            required=True,
            empty_label=None,
            help_text=_(
                "Please select a project of your organisation and click select."
            ),
        )


class CommunicationContentCreationForm(forms.Form):

    sizes = None

    def __init__(self, project=None, format=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sizes = SOCIAL_MEDIA_SIZES[format]

        self.fields["title"] = forms.CharField(
            max_length=self.sizes["title_max_length"],
            label=_("Title"),
            required=True,
            help_text=_(
                "This title will be displayed as a header. "
                "It should be max. {} characters long."
            ).format(self.sizes["title_max_length"]),
        )
        self.fields["description"] = forms.CharField(
            max_length=self.sizes["description_max_length"],
            label=_("Description"),
            required=True,
            help_text=_(
                "This description will be displayed below "
                "the title. It should briefly state the goal "
                "of the project in max. {} chars."
            ).format(self.sizes["description_max_length"]),
        )

        self.fields["image"] = forms.ImageField(
            label=_("Picture Upload"),
            required=True,
            widget=ImageInputWidgetSimple,
            help_text=_(
                "The picture will be displayed in the sharepic. It "
                "must be min. {} pixel wide and {} pixel tall. "
                "Allowed file formats are png, jpeg, gif. The file "
                "size should be max. 5 MB."
            ).format(self.sizes["img_min_width"], self.sizes["img_min_height"]),
        )

        self.fields["add_aplus_logo"] = forms.BooleanField(required=False, initial=True)

        self.fields["add_orga_logo"] = forms.BooleanField(required=False, initial=True)

        if project:
            self.fields["title"].initial = project.name[
                : self.sizes["title_max_length"]
            ]
            self.fields["description"].initial = project.description[
                : self.sizes["description_max_length"]
            ]

    def clean_image(self):
        image = self.cleaned_data["image"]
        errors = []
        image_max_mb = 5
        image_max_size = image_max_mb * 10**6

        if image.size > image_max_size:
            msg = _("Image should be at most {max_size} MB")
            errors.append(ValidationError(msg.format(max_size=image_max_mb)))

        if hasattr(image, "width"):
            image_width = image.width
        else:
            image_width = image.image.width
        if image_width < self.sizes["img_min_width"]:
            msg = _("Image must be at least {min_width} pixels wide")
            errors.append(
                ValidationError(msg.format(min_width=self.sizes["img_min_width"]))
            )

        if hasattr(image, "height"):
            image_height = image.height
        else:
            image_height = image.image.height
        if image_height < self.sizes["img_min_height"]:
            msg = _("Image must be at least {min_height} pixels high")
            errors.append(
                ValidationError(msg.format(min_height=self.sizes["img_min_height"]))
            )

        if errors:
            raise ValidationError(errors)
        return image
