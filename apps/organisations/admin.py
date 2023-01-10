from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib import admin
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm

from . import models


class MemberInline(admin.TabularInline):
    model = models.Member
    fields = [
        "member",
    ]
    raw_id_fields = ("member",)
    extra = 1


class OrganisationAdminForm(TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["information"].widget = CKEditorUploadingWidget(
            config_name="collapsible-image-editor"
        )

    class Meta:
        model = models.Organisation
        fields = "__all__"


@admin.register(models.Organisation)
class OrganisationAdmin(TranslatableAdmin):
    form = OrganisationAdminForm
    search_fields = ("name", "slug")
    list_display = ("id", "name", "slug", "site")
    raw_id_fields = ("initiators",)
    inlines = [
        MemberInline,
    ]
    fieldsets = (
        (None, {"fields": ("name", "initiators", "title")}),
        (
            "Translations",
            {
                "fields": ("description", "slogan", "information"),
            },
        ),
        (
            "Images",
            {
                "classes": ("collapse",),
                "fields": ("logo", "image", "image_copyright"),
            },
        ),
        (
            "Website and social media",
            {
                "classes": ("collapse",),
                "fields": (
                    "url",
                    "twitter_handle",
                    "facebook_handle",
                    "instagram_handle",
                ),
            },
        ),
        (
            "Legal information",
            {
                "classes": ("collapse",),
                "fields": ("imprint", "terms_of_use", "data_protection", "netiquette"),
            },
        ),
        (
            "Settings",
            {
                "fields": ("is_supporting", "language", "site"),
            },
        ),
    )


@admin.register(models.Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "organisation", "member")
    raw_id_fields = ("member",)


@admin.register(models.OrganisationTermsOfUse)
class OrganisationTermsOfUseAdmin(admin.ModelAdmin):
    list_display = ("id", "organisation", "user", "has_agreed")
    list_filter = ("organisation",)

    def has_add_permission(self, request, obj=None):
        return False
