from django.db import models

from adhocracy4.models import base
from adhocracy4.projects.models import Project


class Insight(base.TimeStampedModel):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    active_participants = models.IntegerField()
    comments = models.IntegerField()
    ratings = models.IntegerField()
    written_ideas = models.IntegerField()
    poll_answers = models.IntegerField()
    interactive_events = models.IntegerField()
    display = models.BooleanField(default=False)

    def __str__(self):
        return "Insights for project %s" % self.project.name
