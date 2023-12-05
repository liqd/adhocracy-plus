from autoslug import AutoSlugField
from ckeditor.fields import RichTextField
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from adhocracy4 import transforms
from adhocracy4.categories.fields import CategoryField
from adhocracy4.comments import models as comment_models
from adhocracy4.images.fields import ConfiguredImageField
from adhocracy4.labels import models as labels_models
from adhocracy4.models import query
from adhocracy4.modules import models as module_models
from adhocracy4.ratings import models as rating_models
from apps.moderatorfeedback.models import Moderateable
from apps.moderatorremark import models as remark_models


class BuyableQuerySet(models.QuerySet):
    def annotate_choin_sum(self):
        from django.db.models import F
        from django.db.models import Value
        from django.db.models.functions import Coalesce

        return self.annotate(
            choin_sum=Coalesce(
                F("ideachoin__choins"), Value(0), output_field=models.FloatField()
            )
        )

    def annotate_remaining_choins(self):
        from django.db.models import Case
        from django.db.models import ExpressionWrapper
        from django.db.models import F
        from django.db.models import FloatField
        from django.db.models import IntegerField
        from django.db.models import Q
        from django.db.models import Value
        from django.db.models import When
        from django.db.models.functions import Coalesce

        return self.annotate(
            remaining_choins=Case(
                When(
                    ~Q(moderator_status="ACCEPTED"),
                    then=ExpressionWrapper(
                        (
                            Coalesce(
                                F("ideachoin__goal"),
                                Value(0),
                                output_field=FloatField(),
                            )
                            - Coalesce(
                                F("choin_sum"), Value(0), output_field=FloatField()
                            )
                        )
                        / Case(
                            When(
                                Q(positive_rating_count__gt=0),
                                then=F("positive_rating_count"),
                            ),
                            default=Value(1),
                            output_field=IntegerField(),
                        ),
                        output_field=FloatField(),
                    ),
                ),
                default=Value(0),
                output_field=FloatField(),
            )
        )


class IdeaQuerySet(query.RateableQuerySet, query.CommentableQuerySet, BuyableQuerySet):
    pass


class AbstractIdea(module_models.Item, Moderateable):
    item_ptr = models.OneToOneField(
        to=module_models.Item,
        parent_link=True,
        related_name="%(app_label)s_%(class)s",
        on_delete=models.CASCADE,
    )
    slug = AutoSlugField(populate_from="name", unique=True)
    name = models.CharField(max_length=120, verbose_name=_("Title"))
    description = RichTextField(verbose_name=_("Description"))
    image = ConfiguredImageField(
        "idea_image",
        verbose_name=_("Add image"),
        upload_to="ideas/images",
        blank=True,
        help_prefix=_("Visualize your idea."),
    )
    category = CategoryField()

    labels = models.ManyToManyField(
        labels_models.Label,
        verbose_name=_("Labels"),
        related_name=("%(app_label)s_" "%(class)s_label"),
    )

    objects = IdeaQuerySet.as_manager()

    @property
    def reference_number(self):
        return "{:d}-{:05d}".format(self.created.year, self.pk)

    @property
    def remark(self):
        content_type = ContentType.objects.get_for_model(self)
        return remark_models.ModeratorRemark.objects.filter(
            item_content_type=content_type, item_object_id=self.id
        ).first()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.description = transforms.clean_html_field(self.description)
        super().save(*args, **kwargs)


class Idea(AbstractIdea):
    ratings = GenericRelation(
        rating_models.Rating, related_query_name="idea", object_id_field="object_pk"
    )
    comments = GenericRelation(
        comment_models.Comment, related_query_name="idea", object_id_field="object_pk"
    )

    def get_absolute_url(self):
        return reverse(
            "a4_candy_ideas:idea-detail",
            kwargs=dict(
                organisation_slug=self.project.organisation.slug,
                pk="{:05d}".format(self.pk),
                year=self.created.year,
            ),
        )

    class Meta:
        ordering = ["-created"]
