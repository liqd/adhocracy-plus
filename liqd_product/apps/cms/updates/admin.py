from django.contrib import admin

from liqd_product.apps.cms.updates.models import KeepMeUpdatedEmail


class KeepMeUpdatedEmailAdmin(admin.ModelAdmin):
    list_filter = (
        'interested_as_municipality',
        'interested_as_citizen',
    )


admin.site.register(KeepMeUpdatedEmail, KeepMeUpdatedEmailAdmin)
