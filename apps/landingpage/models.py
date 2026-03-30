from django.db import models


class StatisticsItem(models.Model):
    ITEM_TYPES = [
        ("text", "Text Stat"),
        ("testimonial", "Testimonial"),
        ("image", "Image"),
    ]

    order = models.PositiveIntegerField(default=0)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)

    # Text fields
    header = models.CharField(max_length=200, blank=True)
    subheader = models.CharField(max_length=300, blank=True)

    # Testimonial fields
    quote = models.TextField(blank=True)
    person_name = models.CharField(max_length=100, blank=True)
    person_description = models.CharField(max_length=200, blank=True)
    person_image = models.ImageField(upload_to="testimonials/", blank=True, null=True)

    # Image fields
    image = models.ImageField(upload_to="statistics/", blank=True, null=True)
    image_alt_text = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]
