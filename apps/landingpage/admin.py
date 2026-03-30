from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import StatisticsItem


class StatisticsItemForm(forms.ModelForm):
    class Meta:
        model = StatisticsItem
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        item_type = cleaned_data.get("item_type")

        if item_type == "text":
            if not cleaned_data.get("header"):
                self.add_error("header", "Header is required for text statistics.")
        elif item_type == "testimonial":
            if not cleaned_data.get("quote"):
                self.add_error("quote", "Quote is required for testimonials.")
            if not cleaned_data.get("person_name"):
                self.add_error(
                    "person_name", "Person name is required for testimonials."
                )
        elif item_type == "image":
            if not cleaned_data.get("image"):
                self.add_error("image", "Image is required for image statistics.")

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
            "Text Statistics",
            {
                "fields": ("header", "subheader"),
                "classes": ("collapse",),
            },
        ),
        (
            "Testimonial",
            {
                "fields": (
                    "quote",
                    "person_name",
                    "person_description",
                    "person_image",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Image Statistics",
            {
                "fields": ("image", "image_alt_text"),
                "classes": ("collapse",),
            },
        ),
    )

    def preview(self, obj):
        if obj.item_type == "text":
            return obj.header
        elif obj.item_type == "testimonial":
            return f"{obj.quote[:50]}... - {obj.person_name}"
        elif obj.item_type == "image":
            if obj.image:
                return format_html(
                    '<img src="{}" width="40" height="40" />', obj.image.url
                )
            return "No image"
        return "-"

    preview.short_description = "Preview"
