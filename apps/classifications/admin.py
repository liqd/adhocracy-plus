from django.contrib import admin

from . import models

admin.site.register(models.UserClassification)
admin.site.register(models.AIClassification)
