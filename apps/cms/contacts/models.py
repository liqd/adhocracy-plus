from django.conf import settings
from django.contrib import messages
from django.db import models
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel
from wagtail.admin.panels import FieldRowPanel
from wagtail.admin.panels import MultiFieldPanel
from wagtail.admin.panels import ObjectList
from wagtail.admin.panels import TabbedInterface
from wagtail.admin.panels import TitleFieldPanel
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.models import AbstractEmailForm
from wagtail.contrib.forms.models import AbstractFormField
from wagtail.contrib.forms.models import AbstractFormSubmission
from wagtail.fields import RichTextField

from apps.captcha.fields import ProsopoCaptchaField
from apps.cms.emails import AnswerToContactFormEmail
from apps.cms.settings import helpers
from apps.contrib.translations import TranslatedField
from apps.users.forms import PROSOPO_CAPTCHA_HELP


class FormField(AbstractFormField):
    page = ParentalKey("FormPage", on_delete=models.CASCADE, related_name="form_fields")


class WagtailCaptchaFormBuilder(FormBuilder):
    @property
    def formfields(self):
        fields = super().formfields
        # Add captcha to formfields property if Prosopo is configured
        if (
            hasattr(settings, "PROSOPO_SITE_KEY")
            and settings.PROSOPO_SITE_KEY
            and hasattr(settings, "PROSOPO_SECRET_KEY")
            and settings.PROSOPO_SECRET_KEY
        ):
            fields["captcha"] = ProsopoCaptchaField(
                label=_("I am not a robot"),
                help_text=helpers.add_email_link_to_helptext("", PROSOPO_CAPTCHA_HELP),
            )

        return fields


class WagtailCaptchaEmailForm(AbstractEmailForm):
    """For pages implementing AbstractEmailForms with captcha."""

    form_builder = WagtailCaptchaFormBuilder

    class Meta:
        abstract = True


class CustomFormSubmission(AbstractFormSubmission):
    email = models.EmailField()
    message = models.TextField()
    telephone_number = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100, blank=True)

    def get_data(self):
        form_data = super().get_data()
        form_data.update(
            {
                "email": self.email,
                "message": self.message,
                "telephone_number": self.telephone_number,
                "name": self.name,
            }
        )

        return form_data


class FormPage(WagtailCaptchaEmailForm):
    header_de = models.CharField(max_length=500, blank=True, verbose_name="Header")
    header_en = models.CharField(max_length=500, blank=True, verbose_name="Header")

    intro_en = RichTextField(blank=True)
    intro_de = RichTextField(blank=True)

    thank_you_text_en = models.TextField(blank=True)
    thank_you_text_de = models.TextField(blank=True)

    contact_person_name = models.CharField(max_length=100, blank=True)

    contact_person_image = models.ForeignKey(
        "a4_candy_cms_images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Image of contact person",
        help_text="The Image will be shown " "besides the name of the contact person",
    )

    header = TranslatedField("header_de", "header_en")

    intro = TranslatedField("intro_de", "intro_en")

    thank_you_text = TranslatedField("thank_you_text_de", "thank_you_text_en")

    def get_submission_class(self):
        return CustomFormSubmission

    def process_form_submission(self, form):
        form.fields.pop("captcha", None)
        form.cleaned_data.pop("captcha", None)
        data = form.cleaned_data
        submission = self.get_submission_class().objects.create(
            form_data=form.cleaned_data,
            page=self,
            email=data["email"],
            message=data["message"],
            telephone_number=data["telephone_number"],
            name=data["name"],
        )
        if self.to_address:
            self.send_mail(form)
        if form.cleaned_data["receive_copy"]:
            AnswerToContactFormEmail.send(submission)
        return submission

    def render_landing_page(self, request, form_submission=None, *args, **kwargs):
        if "Referer" in request.headers and request.headers.get("Referer"):
            messages.add_message(request, messages.SUCCESS, self.thank_you_text)
            return redirect(request.headers["Referer"])
        return super().render_landing_page(request, form_submission, *args, **kwargs)

    def get_form_fields(self):
        fields = list(super().get_form_fields())
        fields.insert(
            0,
            FormField(
                label="receive_copy",
                clean_name="receive_copy",
                field_type="checkbox",
                help_text=_("I want to receive a copy of my message"),
                required=False,
            ),
        )

        fields.insert(
            0,
            FormField(
                label="message",
                clean_name="message",
                help_text=_("Your message"),
                field_type="multiline",
                required=True,
            ),
        )

        fields.insert(
            0,
            FormField(
                label="email",
                clean_name="email",
                help_text=_("Your email address"),
                field_type="email",
                required=True,
            ),
        )

        fields.insert(
            0,
            FormField(
                label="telephone_number",
                clean_name="telephone_number",
                help_text=_("Your telephone number"),
                field_type="singleline",
                required=False,
            ),
        )

        fields.insert(
            0,
            FormField(
                label="name",
                clean_name="name",
                help_text=_("Your name"),
                field_type="singleline",
                required=False,
            ),
        )
        return fields

    en_content_panels = [
        FieldPanel("header_en"),
        FieldPanel("intro_en"),
        FieldPanel("thank_you_text_en"),
    ]

    de_content_panels = [
        FieldPanel("header_de"),
        FieldPanel("intro_de"),
        FieldPanel("thank_you_text_de"),
    ]

    common_panels = [
        TitleFieldPanel("title"),
        FieldPanel("slug"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address", classname="col6"),
                        FieldPanel("to_address", classname="col6"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            "Email",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("contact_person_name", classname="col6"),
                        FieldPanel("contact_person_image", classname="col6"),
                    ]
                ),
            ],
            "Contact Person",
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(common_panels, heading="Common"),
            ObjectList(en_content_panels, heading="English"),
            ObjectList(de_content_panels, heading="German"),
        ]
    )
