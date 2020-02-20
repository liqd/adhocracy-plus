from autoslug import AutoSlugField
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from adhocracy4.comments import models as comment_models
from adhocracy4.models import query
from adhocracy4.modules import models as module_models


class SubjectQuerySet(query.CommentableQuerySet):
    pass


class Subject(module_models.Item):
    slug = AutoSlugField(populate_from='name', unique=True)
    name = models.CharField(
        max_length=120,
        verbose_name=_('Title'),
        help_text=_('max 120 characters')
    )
    description = models.CharField(
        max_length=350,
        blank=True,
        verbose_name=_('Description'),
        help_text=_('In addition to the title, you can insert an optional '
                    'explanatory text (max. 350 char.). This field is only '
                    'shown in the participation if it is filled out.')
    )

    comments = GenericRelation(comment_models.Comment,
                               related_query_name='subject',
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

    @cached_property
    def comment_creator_count(self):
        creators = self.comments.values_list('creator', flat=True)
        comment_creator_count = len(list(set(creators)))
        return comment_creator_count

    @cached_property
    def comment_creator_count_minus_three(self):
        if self.comment_creator_count <= 3:
            return None
        else:
            return self.comment_creator_count - 3

    @cached_property
    def last_three_creators(self):
        comments = (
            self.comments.all().select_related('creator').order_by('-created')
        )
        last_three_creators = []
        if comments:
            for comment in comments:
                if comment.creator not in last_three_creators \
                        and not (comment.is_censored or comment.is_removed):
                    last_three_creators.append(comment.creator)
                if len(last_three_creators) >= 3:
                    return last_three_creators
        return last_three_creators
