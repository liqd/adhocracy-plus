import base64
import json
import os
from io import BytesIO

from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.generic import DetailView
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from adhocracy4.dashboard import mixins as a4dashboard_mixins
from apps.projects.models import Project

from . import forms
from .forms import SOCIAL_MEDIA_SIZES
from .forms import CommunicationContentCreationForm
from .models import Organisation


class OrganisationView(DetailView):
    template_name = "a4_candy_organisations/organisation_landing_page.html"
    model = Organisation
    slug_url_kwarg = "organisation_slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active, future, past = self.object.get_projects_list(self.request.user)

        context["active_projects"] = active
        context["future_projects"] = future
        context["past_projects"] = past

        project_headline = ""
        if active:
            project_headline = _("Participate now!")
        elif future:
            project_headline = _("Upcoming participation")
        elif past:
            project_headline = _("Ended participation")
        context["project_headline"] = project_headline

        return context


class InformationView(DetailView):
    template_name = "a4_candy_organisations/organisation_information.html"
    model = Organisation
    slug_url_kwarg = "organisation_slug"


class ImprintView(DetailView):
    template_name = "a4_candy_organisations/organisation_imprint.html"
    model = Organisation
    slug_url_kwarg = "organisation_slug"


class TermsOfUseView(DetailView):
    template_name = "a4_candy_organisations/organisation_terms_of_use.html"
    model = Organisation
    slug_url_kwarg = "organisation_slug"


class NetiquetteView(DetailView):
    template_name = "a4_candy_organisations/organisation_netiquette.html"
    model = Organisation
    slug_url_kwarg = "organisation_slug"


class DataProtectionView(DetailView):
    template_name = "a4_candy_organisations/organisation_data_protection.html"
    model = Organisation
    slug_url_kwarg = "organisation_slug"


class DashboardOrganisationUpdateView(
    a4dashboard_mixins.DashboardBaseMixin, SuccessMessageMixin, generic.UpdateView
):
    model = Organisation
    form_class = forms.OrganisationForm
    slug_url_kwarg = "organisation_slug"
    template_name = "a4_candy_organisations/organisation_form.html"
    success_message = _("Organisation information successfully updated.")
    permission_required = "a4_candy_organisations.change_organisation"
    menu_item = "organisation"

    def get_permission_object(self):
        return self.organisation

    def get_success_url(self):
        return self.request.path

    def get_project_languages(self):
        languages = getattr(settings, "LANGUAGES", None)
        if languages:
            language_dict = dict((x, str(y)) for x, y in languages)
            return json.dumps(language_dict)
        else:
            raise ImproperlyConfigured("set LANGUAGES in settings")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["language_dict"] = self.get_project_languages()
        return context


class DashboardLegalInformationUpdateView(
    a4dashboard_mixins.DashboardBaseMixin, SuccessMessageMixin, generic.UpdateView
):
    model = Organisation
    form_class = forms.OrganisationLegalInformationForm
    slug_url_kwarg = "organisation_slug"
    template_name = "a4_candy_organisations/organisation_form_legal_info.html"
    success_message = _("Legal information successfully updated.")
    permission_required = "a4_candy_organisations.change_organisation"
    menu_item = "organisation"

    def get_permission_object(self):
        return self.organisation

    def get_success_url(self):
        return self.request.path


class DashboardCommunicationProjectChoiceView(
    a4dashboard_mixins.DashboardBaseMixin, generic.FormView
):

    menu_item = "communication"
    form_class = forms.CommunicationProjectChoiceForm
    permission_required = "a4_candy_organisations.change_organisation"
    template_name = "a4_candy_organisations/" "communication_form_social_media.html"
    slug_url_kwarg = "organisation_slug"

    def get_permission_object(self):
        return self.organisation

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organisation"] = self.organisation
        return kwargs

    def form_valid(self, form):
        """If the form is valid, redirect to the content creation form."""
        project = form.cleaned_data["project"]
        img_format = form.cleaned_data["format"]
        return redirect(
            reverse(
                "a4dashboard:communication-content-create",
                kwargs={
                    "organisation_slug": self.organisation.slug,
                    "project_slug": project.slug,
                    "format": int(img_format),
                },
            )
        )

    def get_context_data(self, **kwargs):
        """Insert the form as project_form into the context dict."""
        kwargs = super().get_context_data(**kwargs)
        if "form" in kwargs:
            kwargs.pop("form")
        if "project_form" not in kwargs:
            kwargs["project_form"] = self.get_form()
        if "organisation" not in kwargs:
            kwargs["organisation"] = self.organisation

        return kwargs


class DashboardCommunicationContentCreateView(
    a4dashboard_mixins.DashboardBaseMixin, generic.FormView
):

    menu_item = "communication"
    form_class = forms.CommunicationContentCreationForm
    permission_required = "a4_candy_organisations.change_organisation"
    template_name = "a4_candy_organisations/" "communication_form_social_media.html"
    slug_url_kwarg = "organisation_slug"

    def get_permission_object(self):
        return self.organisation

    def get_success_url(self):
        return self.request.path

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not self.request.POST:
            kwargs["project"] = self.project
        kwargs["format"] = self.format

        return kwargs

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        if "form" in kwargs:
            kwargs.pop("form")
        if "content_form" not in kwargs:
            kwargs["content_form"] = self.get_form()
        if "project_form" not in kwargs:
            project_form = forms.CommunicationProjectChoiceForm(
                initial={"project": self.project, "format": self.format},
                organisation=self.organisation,
            )
            kwargs["project_form"] = project_form
        if "organisation" not in kwargs:
            kwargs["organisation"] = self.organisation

        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data
        context = self.get_context_data()
        img = self.generate_image(data)
        # get the content form with unchanged cleaned data, as image generation
        # changes the image data (why?)
        content_form = CommunicationContentCreationForm(
            initial=data, project=self.project, format=self.format
        )
        context["image_preview"] = img
        context["content_form"] = content_form
        return self.render_to_response(context)

    @staticmethod
    def calc_aspect_ratio(width, height, req_width, req_height):
        # calculate aspect_ratio
        aspect_ratio = width / float(height)
        required_ratio = req_width / float(req_height)
        if aspect_ratio > required_ratio:
            new_width = int(required_ratio * height)
            offset = (width - new_width) / 2
            resize = (offset, 0, width - offset, height)
        else:
            new_height = int(width / required_ratio)
            offset = (height - new_height) / 2
            resize = (0, offset, width, height - offset)
        return resize

    def generate_image(self, data):
        # Get required image size and image
        sharepic_format = SOCIAL_MEDIA_SIZES[self.format]
        req_width = sharepic_format["img_min_width"]
        req_height = sharepic_format["img_min_height"]

        image_get = Image.open(data["image"].file)
        width, height = image_get.size
        resize = self.calc_aspect_ratio(width, height, req_width, req_height)
        # Use LANCZOS for resampling to keep better quality
        image = image_get.crop(resize).resize(
            (req_width, req_height), Image.Resampling.LANCZOS
        )

        # get required total size and add appropriate padding
        result = Image.new(
            image.mode,
            (sharepic_format["img_min_width"], sharepic_format["overall_height"]),
            (255, 255, 255),
        )
        result.paste(image, (0, 0))

        # image is converted into editable form using Draw function
        image = ImageDraw.Draw(result)

        # text dimension, color and font
        font = ImageFont.truetype(
            os.path.join(
                settings.BASE_DIR,
                "adhocracy-plus/assets/fonts/SourceSansPro-Semibold.otf",
            ),
            sharepic_format["title_size"],
        )
        fontsm = ImageFont.truetype(
            os.path.join(
                settings.BASE_DIR,
                "adhocracy-plus/assets/fonts/SourceSansPro-Regular.otf",
            ),
            sharepic_format["description_size"],
        )
        title = data["title"]
        description = data["description"]
        title_width = image.textlength(title, font=font)
        description_width = image.textlength(description, font=fontsm)
        # add text using width to center
        image.text(
            (
                (sharepic_format["img_min_width"] - title_width) / 2,
                sharepic_format["title_y"],
            ),
            title,
            fill=(0, 0, 0),
            font=font,
        )
        image.text(
            (
                (sharepic_format["img_min_width"] - description_width) / 2,
                sharepic_format["description_y"],
            ),
            description,
            fill=(0, 0, 0),
            font=fontsm,
        )

        if data["add_orga_logo"] and self.organisation.logo:
            # get organisations logo
            logo_org_get = Image.open(self.organisation.logo)
            logo_org_size = (144, 144)
            logo_org = logo_org_get.resize(logo_org_size)
            border = 8
            logo_org_result = Image.new(
                image.mode,
                ((border + 144 + border), (border + 144 + border)),
                (255, 255, 255),
            )
            logo_org_result.paste(logo_org, (border, border))
            result.paste(logo_org_result, (80, sharepic_format["org_logo_y"]))

        if data["add_aplus_logo"]:
            # get aplus logo
            logo_aplus_get = Image.open(
                os.path.join(settings.BASE_DIR, "adhocracy-plus/assets/images/logo.png")
            )
            logo_aplus_size = (
                sharepic_format["aplus_logo_width"],
                sharepic_format["aplus_logo_height"],
            )
            logo_aplus = logo_aplus_get.resize(logo_aplus_size)
            # position a+ logo
            logo2_offset_y = sharepic_format["aplus_logo_y"]
            logo2_offset_x = (
                sharepic_format["img_min_width"] - sharepic_format["aplus_logo_width"]
            ) // 2
            result.paste(logo_aplus, (logo2_offset_x, logo2_offset_y), mask=logo_aplus)

        buffered_image = BytesIO()
        result.save(buffered_image, format="PNG")

        return base64.b64encode(buffered_image.getvalue()).decode("utf-8")

    @property
    def project(self):
        return get_object_or_404(Project, slug=self.kwargs["project_slug"])

    @property
    def format(self):
        return self.kwargs["format"]
