from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from adhocracy4.categories import models as category_models
from adhocracy4.dashboard import DashboardComponent
from adhocracy4.dashboard import ModuleFormSetComponent
from adhocracy4.dashboard import components

from . import forms
from . import views


class MediaComponent(DashboardComponent):
    identifier = "extra_fields"
    weight = 20
    label = _("Media")

    def is_effective(self, module):
        return module.blueprint_type == "IE"

    def get_progress(self, module):
        return 0, 0

    def get_base_url(self, module):
        return reverse(
            "a4dashboard:interactiveevents-media",
            kwargs={
                "organisation_slug": module.project.organisation.slug,
                "module_slug": module.slug,
            },
        )

    def get_urls(self):
        return [
            (
                r"^modules/(?P<module_slug>[-\w_]+)/media/$",
                views.ExtraFieldsDashboardView.as_view(component=self),
                "interactiveevents-media",
            )
        ]


class ModuleAffiliationsComponent(ModuleFormSetComponent):
    identifier = "affiliations"
    weight = 13
    label = _("Affiliations")

    form_title = _("Edit affiliations")
    form_class = forms.AffiliationFormSet
    form_template_name = (
        "a4_candy_interactive_events/includes/module_affiliations_form.html"
    )

    def get_progress(self, module):
        if category_models.Category.objects.filter(module=module).exists():
            return 1, 1
        return 0, 1

    def is_effective(self, module):
        return module.blueprint_type == "IE"


components.register_module(MediaComponent())
components.register_module(ModuleAffiliationsComponent())
