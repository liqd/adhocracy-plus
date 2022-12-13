import base64
import json
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
from .models import Organisation


class OrganisationView(DetailView):
    template_name = 'a4_candy_organisations/organisation_landing_page.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active, future, past = \
            self.object.get_projects_list(self.request.user)

        context['active_projects'] = active
        context['future_projects'] = future
        context['past_projects'] = past

        project_headline = ''
        if active:
            project_headline = _('Participate now!')
        elif future:
            project_headline = _('Upcoming participation')
        elif past:
            project_headline = _('Ended participation')
        context['project_headline'] = project_headline

        return context


class InformationView(DetailView):
    template_name = 'a4_candy_organisations/organisation_information.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'


class ImprintView(DetailView):
    template_name = 'a4_candy_organisations/organisation_imprint.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'


class TermsOfUseView(DetailView):
    template_name = 'a4_candy_organisations/organisation_terms_of_use.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'


class NetiquetteView(DetailView):
    template_name = 'a4_candy_organisations/organisation_netiquette.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'


class DataProtectionView(DetailView):
    template_name = 'a4_candy_organisations/organisation_data_protection.html'
    model = Organisation
    slug_url_kwarg = 'organisation_slug'


class DashboardOrganisationUpdateView(a4dashboard_mixins.DashboardBaseMixin,
                                      SuccessMessageMixin,
                                      generic.UpdateView):
    model = Organisation
    form_class = forms.OrganisationForm
    slug_url_kwarg = 'organisation_slug'
    template_name = 'a4_candy_organisations/organisation_form.html'
    success_message = _('Organisation information successfully updated.')
    permission_required = 'a4_candy_organisations.change_organisation'
    menu_item = 'organisation'

    def get_permission_object(self):
        return self.organisation

    def get_success_url(self):
        return self.request.path

    def get_project_languages(self):
        languages = getattr(settings, 'LANGUAGES', None)
        if languages:
            language_dict = dict((x, str(y)) for x, y in languages)
            return json.dumps(language_dict)
        else:
            raise ImproperlyConfigured('set LANGUAGES in settings')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['language_dict'] = self.get_project_languages()
        return context


class DashboardLegalInformationUpdateView(
        a4dashboard_mixins.DashboardBaseMixin,
        SuccessMessageMixin,
        generic.UpdateView):
    model = Organisation
    form_class = forms.OrganisationLegalInformationForm
    slug_url_kwarg = 'organisation_slug'
    template_name = 'a4_candy_organisations/organisation_form_legal_info.html'
    success_message = _('Legal information successfully updated.')
    permission_required = 'a4_candy_organisations.change_organisation'
    menu_item = 'organisation'

    def get_permission_object(self):
        return self.organisation

    def get_success_url(self):
        return self.request.path


class DashboardCommunicationProjectChoiceView(
        a4dashboard_mixins.DashboardBaseMixin,
        generic.FormView):

    menu_item = 'communication'
    form_class = forms.CommunicationProjectChoiceForm
    permission_required = 'a4_candy_organisations.change_organisation'
    template_name = 'a4_candy_organisations/' \
                    'communication_form_social_media.html'
    slug_url_kwarg = 'organisation_slug'

    def get_permission_object(self):
        return self.organisation

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organisation'] = self.organisation
        return kwargs

    def form_valid(self, form):
        """If the form is valid, redirect to the content creation form."""
        project = form.cleaned_data['project']
        img_format = form.cleaned_data['format']
        return redirect(
            reverse('a4dashboard:communication-content-create',
                    kwargs={'organisation_slug': self.organisation.slug,
                            'project_slug': project.slug,
                            'format': int(img_format)
                            }))

    def get_context_data(self, **kwargs):
        """Insert the form as project_form into the context dict."""
        kwargs = super().get_context_data(**kwargs)
        if 'form' in kwargs:
            kwargs.pop('form')
        if 'project_form' not in kwargs:
            kwargs['project_form'] = self.get_form()
        if 'organisation' not in kwargs:
            kwargs['organisation'] = self.organisation

        return kwargs


class DashboardCommunicationContentCreateView(
        a4dashboard_mixins.DashboardBaseMixin,
        generic.FormView):

    menu_item = 'communication'
    form_class = forms.CommunicationContentCreationForm
    permission_required = 'a4_candy_organisations.change_organisation'
    template_name = 'a4_candy_organisations/' \
                    'communication_form_social_media.html'
    slug_url_kwarg = 'organisation_slug'

    def get_permission_object(self):
        return self.organisation

    def get_success_url(self):
        return self.request.path

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not self.request.POST:
            kwargs['project'] = self.project
        kwargs['format'] = self.format

        return kwargs

    def get_context_data(self, **kwargs):
        if 'form' in kwargs:
            kwargs.pop('form')
        if 'content_form' not in kwargs:
            kwargs['content_form'] = self.get_form()
        if 'project_form' not in kwargs:
            project_form = forms.CommunicationProjectChoiceForm(
                initial={'project': self.project,
                         'format': self.format},
                organisation=self.organisation
            )
            kwargs['project_form'] = project_form
        if 'organisation' not in kwargs:
            kwargs['organisation'] = self.organisation

        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        img = self.generate_image(data)
        context = self.get_context_data()
        context['image_preview'] = img
        return self.render_to_response(context)

    def generate_image(self, data):
        # Dummy images
        image = Image.new('RGB', (304, 192), color='red')
        logo1 = Image.new('RGB', (100, 10), color='blue')
        logo2 = Image.new('RGB', (100, 10), color='green')

        # Adding padding
        right = 0
        left = 0
        top = 64
        bottom = 48
        width, height = image.size
        new_width = width + right + left
        new_height = height + top + bottom
        result = Image.new(
            image.mode, (new_width, new_height), (255, 255, 255))
        result.paste(image, (left, top))

        # Adding writting
        # Image is converted into editable form using Draw function and
        # assigned to d1
        d1 = ImageDraw.Draw(result)
        # Text location, color and font
        font = ImageFont.truetype(
            "adhocracy-plus/assets/fonts/SourceSansPro-Semibold.otf", 20)
        fontsm = ImageFont.truetype(
            "adhocracy-plus/assets/fonts/SourceSansPro-Regular.otf", 12)
        d1.text((16, 12), data['title'], fill=(0, 0, 0), font=font)
        d1.text((16, 37), data['description'], fill=(0, 0, 0), font=fontsm)

        # Adding logos
        result.paste(logo1, (46, 277))
        result.paste(logo2, (157, 277))

        buffered_image = BytesIO()
        result.save(buffered_image, format='PNG')

        return base64.b64encode(buffered_image.getvalue()).decode('utf-8')

    @property
    def project(self):
        return get_object_or_404(Project, slug=self.kwargs['project_slug'])

    @property
    def format(self):
        return self.kwargs['format']
