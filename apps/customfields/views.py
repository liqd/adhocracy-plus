import json

from django.urls import reverse
from django.views import generic

from adhocracy4.dashboard import mixins as dashboard_mixins
from adhocracy4.projects.mixins import ProjectMixin

from .models import CustomFieldSettings


class CustomFieldSettingsDashboardView(
    ProjectMixin,
    dashboard_mixins.DashboardBaseMixin,
    dashboard_mixins.DashboardComponentMixin,
    generic.TemplateView,
):
    template_name = "a4_candy_customfields/custom_field_settings.html"
    permission_required = "a4projects.change_project"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings = self.get_or_create_settings()
        context["widget_attributes"] = json.dumps(
            {
                "settingsId": settings.pk,
                "apiUrl": reverse("custom-fields-detail", kwargs={"pk": settings.pk}),
            }
        )
        return context

    def get_or_create_settings(self):
        try:
            return CustomFieldSettings.objects.get(module=self.module)
        except CustomFieldSettings.DoesNotExist:
            return CustomFieldSettings.objects.create(module=self.module)

    def get_permission_object(self):
        return self.project
