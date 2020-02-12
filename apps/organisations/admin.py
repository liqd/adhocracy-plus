from django.contrib import admin

from . import models


class MemberInline(admin.TabularInline):
    model = models.Member
    fields = [
        'member',
    ]
    raw_id_fields = ('member',)
    extra = 1


@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = (
        'id', 'name'
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
