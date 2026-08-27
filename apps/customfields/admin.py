from django.contrib import admin

from . import models


class CustomFieldChoiceInline(admin.TabularInline):
    model = models.CustomFieldChoice
    extra = 0


class CustomFieldInline(admin.TabularInline):
    model = models.CustomField
    extra = 0


@admin.register(models.CustomFieldSettings)
class CustomFieldSettingsAdmin(admin.ModelAdmin):
    inlines = [CustomFieldInline]


@admin.register(models.CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    inlines = [CustomFieldChoiceInline]
    list_display = ("label", "type", "required", "settings")


@admin.register(models.CustomFieldAnswer)
class CustomFieldAnswerAdmin(admin.ModelAdmin):
    list_display = ("idea", "field", "value")
