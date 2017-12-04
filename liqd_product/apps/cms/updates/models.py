from django.db import models


class KeepMeUpdatedEmail(models.Model):
    interested_as_municipality = models.BooleanField()
    interested_as_citizen = models.BooleanField()
    email = models.EmailField()

    def __str__(self):
        return self.email
