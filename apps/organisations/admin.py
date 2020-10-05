from django.contrib import admin
from parler.admin import TranslatableAdmin

from . import models


class MemberInline(admin.TabularInline):
    model = models.Member
    fields = [
        'member',
    ]
    raw_id_fields = ('member',)
    extra = 1


@admin.register(models.Organisation)
class OrganisationAdmin(TranslatableAdmin):
    search_fields = ('name', 'slug')
    list_display = (
        'id', 'name', 'slug', 'site'
    )
    raw_id_fields = ('initiators',)
    inlines = [
        MemberInline,
    ]


@admin.register(models.Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'id', '__str__', 'organisation', 'member'
    )
    raw_id_fields = ('member',)
