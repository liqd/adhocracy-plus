from django.db import models
from django.utils.translation import get_language


class StatisticsItem(models.Model):
    ITEM_TYPES = [
        ("text", "Text Stat"),
        ("testimonial", "Testimonial"),
        ("image", "Image"),
    ]

    order = models.PositiveIntegerField(default=0)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)

    # Text fields
    header_en = models.CharField(max_length=200, blank=True)
    header_de = models.CharField(max_length=200, blank=True)
    subheader_en = models.CharField(max_length=300, blank=True)
    subheader_de = models.CharField(max_length=300, blank=True)

    # Testimonial fields
    quote_en = models.TextField(blank=True)
    quote_de = models.TextField(blank=True)
    person_name = models.CharField(max_length=100, blank=True)
    person_image = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    person_description_en = models.CharField(max_length=200, blank=True)
    person_description_de = models.CharField(max_length=200, blank=True)

    # Image fields
    image = models.ImageField(upload_to="statistics/", blank=True, null=True)
    image_alt_text_en = models.TextField(blank=True)
    image_alt_text_de = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]

    @property
    def header(self):
        lang = get_language()[:2]
        return getattr(self, f"header_{lang}", self.header_en)

    @property
    def subheader(self):
        lang = get_language()[:2]
        return getattr(self, f"subheader_{lang}", self.subheader_en)

    @property
    def quote(self):
        lang = get_language()[:2]
        return getattr(self, f"quote_{lang}", self.quote_en)

    @property
    def person_description(self):
        lang = get_language()[:2]
        return getattr(self, f"person_description_{lang}", self.person_description_en)

    @property
    def image_alt_text(self):
        lang = get_language()[:2]
        return getattr(self, f"image_alt_text_{lang}", self.image_alt_text_en)
