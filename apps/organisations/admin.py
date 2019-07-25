from django.contrib import admin

from . import models


@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    raw_id_fields = ('initiators',)
