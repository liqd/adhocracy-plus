from autoslug import AutoSlugField
from django.conf import settings
from django.db import models

from liqd_product.apps.partners.models import Partner


class Organisation(models.Model):
    slug = AutoSlugField(populate_from='name', unique=True)
    name = models.CharField(max_length=512)
    initiators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name

    def has_initiator(self, user):
        # FIXME: this is a hack until we adapt all perms to check for partner
        #  admins, too. furthermore it won't help for listing private projects
        #  which is done on the db level based on the initiator relation.
        return (self.initiators.filter(id=user.id).exists() or
                self.partner.has_admin(user))

    def get_absolute_url(self):
        # FIXME: not available yet
        return '#'
