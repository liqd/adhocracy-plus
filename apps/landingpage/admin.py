from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import get_language

from .models import StatisticsItem


class StatisticsItemForm(forms.ModelForm):
    class Meta:
        model = StatisticsItem
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all language-specific fields optional
        lang_fields = [
            "header_de",
            "header_en",
            "subheader_de",
            "subheader_en",
            "quote_de",
            "quote_en",
            "person_description_de",
            "person_description_en",
            "image_alt_text_de",
            "image_alt_text_en",
        ]
        for field in lang_fields:
            if field in self.fields:
                self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()
        item_type = cleaned_data.get("item_type")

        # Get current language or default to English
        lang = get_language()[:2] if get_language() else "en"

        if item_type == "text":
            header_field = f"header_{lang}"
            if not cleaned_data.get(header_field):
                self.add_error(header_field, "Header is required for text statistics.")
        elif item_type == "testimonial":
            quote_field = f"quote_{lang}"
            person_name_field = "person_name"
            if not cleaned_data.get(quote_field):
                self.add_error(quote_field, "Quote is required for testimonials.")
            if not cleaned_data.get(person_name_field):
                self.add_error(
                    person_name_field, "Person name is required for testimonials."
                )
        elif item_type == "image":
            if not cleaned_data.get("image"):
                self.add_error("image", "Image is required for image statistics.")
            alt_text_field = f"image_alt_text_{lang}"
            if not cleaned_data.get(alt_text_field):
                self.add_error(
                    alt_text_field, "Alt text is required for image statistics."
                )

        return cleaned_data


@admin.register(StatisticsItem)
class StatisticsItemAdmin(admin.ModelAdmin):
    form = StatisticsItemForm
    list_display = ["item_type", "preview", "order"]
    list_editable = ["order"]
    list_filter = ["item_type"]

    fieldsets = (
        (None, {"fields": ("item_type", "order")}),
        (
            "Text Statistics (English)",
            {
                "fields": ("header_en", "subheader_en"),
                "classes": ("collapse",),
            },
        ),
        (
            "Text Statistics (German)",
            {
                "fields": ("header_de", "subheader_de"),
                "classes": ("collapse",),
            },
        ),
        (
            "Testimonial (English)",
            {
                "fields": ("quote_en", "person_description_en"),
                "classes": ("collapse",),
            },
        ),
        (
            "Testimonial (German)",
            {
                "fields": ("quote_de", "person_description_de"),
                "classes": ("collapse",),
            },
        ),
        (
            "Testimonial (Shared Fields)",
            {
                "fields": ("person_name", "person_image"),
                "classes": ("collapse",),
            },
        ),
        (
            "Image Statistics",
            {
                "fields": ("image", "image_alt_text_en", "image_alt_text_de"),
                "classes": ("collapse",),
            },
        ),
    )

    def preview(self, obj):
        lang = get_language()[:2] if get_language() else "en"

        if obj.item_type == "text":
            header = getattr(obj, f"header_{lang}", "")
            return header
        elif obj.item_type == "testimonial":
            quote = getattr(obj, f"quote_{lang}", "")
            person_name = obj.person_name
            return f"{quote[:50]}... - {person_name}"
        elif obj.item_type == "image":
            if obj.image:
                return format_html(
                    '<img src="{}" width="40" height="40" />', obj.image.url
                )
            return "No image"
        return "-"

    preview.short_description = "Preview"
