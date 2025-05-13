from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.utils.translation import gettext_lazy as _

from adhocracy4.projects import models
from adhocracy4.projects.admin import ProjectAdminForm


@admin.action(description=_("archive"))
def set_is_archived_true(modeladmin, request, queryset):
    queryset.update(is_archived=True)


@admin.action(description=_("dearchive"))
def set_is_archived_false(modeladmin, request, queryset):
    queryset.update(is_archived=False)


class ProjectAdmin(GISModelAdmin):
    form = ProjectAdminForm
    list_display = ("__str__", "organisation", "is_draft", "is_archived", "created")
    list_filter = ("is_draft", "is_archived", "organisation", "is_app_accessible")
    search_fields = ("name",)
    raw_id_fields = ("moderators", "participants")
    date_hierarchy = "created"
    gis_widget_kwargs = {
        "attrs": {
            "default_zoom": 12,  # Configure zoom level
            "default_lon": 13.404954,
            "default_lat": 52.520008,
        }
    }
    actions = [
        set_is_archived_true,
        set_is_archived_false,
    ]

    fieldsets = (
        (None, {"fields": ("name", "slug", "organisation")}),
        (
            _("Information and result"),
            {
                "fields": ("description", "information", "result"),
            },
        ),
        (
            _("Settings"),
            {
                "classes": ("collapse",),
                "fields": (
                    "access",
                    "is_draft",
                    "is_archived",
                    "is_app_accessible",
                    "moderators",
                    "participants",
                ),
            },
        ),
        (
            _("Images"),
            {
                "classes": ("collapse",),
                "fields": (
                    "image",
                    "image_copyright",
                    "tile_image",
                    "tile_image_copyright",
                ),
            },
        ),
        (
            _("Contact"),
            {
                "classes": ("collapse",),
                "fields": (
                    "contact_name",
                    "contact_address_text",
                    "contact_phone",
                    "contact_email",
                    "contact_url",
                ),
            },
        ),
    )


# Overwrite adhocracy4.projects.admin
admin.site.unregister(models.Project)
admin.site.register(models.Project, ProjectAdmin)
