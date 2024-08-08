from django.contrib import admin

from adhocracy4.modules import admin as module_admin

from . import models


class IdeaAdmin(module_admin.ItemAdmin):
    list_display = ("__str__", "creator", "created", "moderator_status")


admin.site.register(models.Idea, IdeaAdmin)
