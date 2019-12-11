from adhocracy4.projects.mixins import DisplayProjectOrModuleMixin
from apps.ideas import views as idea_views

from . import models


class SubjectListView(idea_views.AbstractIdeaListView,
                      DisplayProjectOrModuleMixin):
    model = models.Subject

    def get_queryset(self):
        return super().get_queryset()\
            .filter(module=self.module) \
            .annotate_comment_count()
