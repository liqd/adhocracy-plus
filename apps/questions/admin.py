from django.contrib import admin

from . import models


class QuestionAdmin(admin.ModelAdmin):
    list_filter = ('module__project', 'module')


admin.site.register(models.Question, QuestionAdmin)
