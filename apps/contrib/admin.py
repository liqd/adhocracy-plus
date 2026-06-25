"""Django Admin for contrib models."""

from django.contrib import admin

from .models import Settings


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ("key", "value_preview", "default_preview")
    search_fields = ("key", "value")
    ordering = ("key",)

    def value_preview(self, obj):
        """Short preview of value (first 80 chars)."""
        if not obj.value:
            return ""
        text = (obj.value or "").strip()
        if len(text) <= 80:
            return text
        return text[:80] + "…"

    value_preview.short_description = "Value (preview)"

    def default_preview(self, obj):
        """Short preview of registry default for this key."""
        default = Settings.get_registry_default(obj.key)
        if default is None:
            return "—"
        text = (default or "").strip()
        if len(text) <= 50:
            return text or "—"
        return text[:50] + "…"

    default_preview.short_description = "Default (preview)"
