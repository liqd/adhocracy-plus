from django.db import models
from django.utils.translation import ugettext_lazy as _


class KeepMeUpdatedEmail(models.Model):
    interested_as_municipality = models.BooleanField(
        verbose_name=_('interested as municipality'))
    interested_as_citizen = models.BooleanField(
        verbose_name=_('interested as citizen'))
    email = models.EmailField()

    def __str__(self):
        return self.email
