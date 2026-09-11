from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from adhocracy4.dashboard import DashboardComponent
from adhocracy4.dashboard import components

from . import views


class CustomFieldComponent(DashboardComponent):
    identifier = "custom_fields"
    weight = 20
    label = _("Custom Fields")

    def is_effective(self, module):
        return module.blueprint_type in ["BS", "IC", "MBS", "MIC"]

    def get_progress(self, module):
        return 0, 0

    def get_base_url(self, module):
        return reverse(
            "a4dashboard:custom-fields-dashboard",
            kwargs={
                "organisation_slug": module.project.organisation.slug,
                "module_slug": module.slug,
            },
        )

    def get_urls(self):
        return [
            (
                r"^modules/(?P<module_slug>[-\w_]+)/custom-fields/$",
                views.CustomFieldSettingsDashboardView.as_view(component=self),
                "custom-fields-dashboard",
            )
        ]


components.register_module(CustomFieldComponent())
