from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable
from wagtail.models import Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from .blocks import LearningContentBlock


@register_snippet
class PermissionLevel(models.Model):
    """Editable permission level that groups learning categories."""

    name = models.CharField(max_length=60, unique=True)
    order = models.IntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Permission Level"
        verbose_name_plural = "Permission Levels"

    def __str__(self):
        return self.name


@register_snippet
class LearningCategory(models.Model):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    permission_level = models.ForeignKey(
        PermissionLevel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="categories",
    )
    order = models.IntegerField(default=0)

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("slug"),
        FieldPanel("permission_level"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Learning Category"
        verbose_name_plural = "Learning Categories"

    def save(self, *args, update_fields=None, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1

            while LearningCategory.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug

        if update_fields:
            update_fields = {"slug"}.union(update_fields)
        super().save(*args, update_fields=update_fields, **kwargs)

    def ordered_nuggets(self):
        """Live, non-private nuggets of this category in display order."""
        return (
            LearningNuggetPage.objects.live()
            .public()
            .select_related("icon")
            .filter(category=self)
            .order_by("order")
        )

    def __str__(self):
        return self.name


class LearningCenterPage(Page):
    """
    Singleton page model for the Learning Center.
    Will contain all learning nuggets organized by category.
    """

    max_count = 1  # Ensures only one instance can be created

    parent_page_types = ["a4_candy_cms_pages.HomePage"]
    subpage_types = ["LearningNuggetPage"]

    class Meta:
        verbose_name = "Learning Center Page"


class LearningNuggetPage(Page, Orderable):
    category = models.ForeignKey(
        LearningCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nuggets",
    )

    icon = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text=_("Upload a PNG icon for this nugget (recommended size: 24x24px)."),
    )

    read_length = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Estimated reading time in minutes."),
    )

    content = StreamField(
        [("learning_nugget", LearningContentBlock())],
        use_json_field=True,
        blank=True,
    )

    search_fields = Page.search_fields + [
        index.SearchField("content"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("category"),
        FieldPanel("icon"),
        FieldPanel("read_length"),
        FieldPanel("content"),
        FieldPanel("order"),
    ]

    parent_page_types = ["LearningCenterPage"]
    subpage_types = []
    order = models.IntegerField(default=0)

    def get_absolute_url(self):
        if self.category:
            return reverse(
                "learning_nuggets:nugget-detail",
                kwargs={"category_slug": self.category.slug, "nugget_slug": self.slug},
            )
        return "#"  # Fallback if no category

    class Meta:
        verbose_name = "Learning Nugget Page"
        ordering = ["order"]
