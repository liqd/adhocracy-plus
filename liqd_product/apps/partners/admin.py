from django.contrib import admin

from . import models


@admin.register(models.Partner)
class PartnerAdmin(admin.ModelAdmin):
    raw_id_fields = ('admins',)
