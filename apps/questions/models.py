from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.urls import reverse

from adhocracy4.categories.fields import CategoryField
from adhocracy4.models.base import TimeStampedModel
from adhocracy4.modules import models as module_models


class AnonymousItem(TimeStampedModel):
    module = models.ForeignKey(module_models.Module, on_delete=models.CASCADE)

    @property
    def project(self):
        return self.module.project

    @property
    def creator(self):
        return AnonymousUser()

    @creator.setter
    def creator(self, value):
        pass

    class Meta:
        abstract = True


class LikeQuerySet(models.QuerySet):

    def annotate_like_count(self):
        return self.annotate(
            like_count=models.Count(
                'question_likes',
                distinct=True
            )
        )


class Question(AnonymousItem):
    text = models.TextField(max_length=1000)
    is_answered = models.BooleanField(default=False)
    is_on_shortlist = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    is_live = models.BooleanField(default=False)

    category = CategoryField()

    objects = LikeQuerySet.as_manager()

    def __str__(self):
        return str(self.text)

    def get_absolute_url(self):
        return reverse('module-detail',
                       args=[str(self.module.project.organisation.slug),
                             str(self.module.slug)])
