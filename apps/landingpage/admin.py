from django.contrib import admin

from .models import StatisticsItem


@admin.register(StatisticsItem)
class StatisticsItemAdmin(admin.ModelAdmin):
    list_display = ["item_type", "header", "person_name", "order"]
    list_editable = ["order"]
