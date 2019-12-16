from django.contrib import admin

from adhocracy4.modules import admin as module_admin

from . import models


class SubjectAdmin(module_admin.ItemAdmin):

    def save_model(self, request, obj, form, change):
        user = request.user
        obj.creator = user
        obj.save()
        super().save_model(request, obj, form, change)


admin.site.register(models.Subject, SubjectAdmin)
