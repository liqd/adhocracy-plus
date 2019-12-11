from autoslug import AutoSlugField
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from adhocracy4.comments import models as comment_models
from adhocracy4.models import query
from adhocracy4.modules import models as module_models


class SubjectQuerySet(query.CommentableQuerySet):
    pass


class Subject(module_models.Item):
    slug = AutoSlugField(populate_from='name', unique=True)
    name = models.CharField(max_length=120, verbose_name=_('Title'))

    comments = GenericRelation(comment_models.Comment,
                               related_query_name='topic',
                               object_id_field='object_pk')

    objects = SubjectQuerySet.as_manager()

    class Meta:
        ordering = ['-created']

    @property
    def reference_number(self):
        return '{:d}-{:05d}'.format(self.created.year, self.pk)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'a4_candy_debate:subject-detail',
            kwargs=dict(
                organisation_slug=self.project.organisation.slug,
                pk='{:05d}'.format(self.pk),
                year=self.created.year
            )
        )
