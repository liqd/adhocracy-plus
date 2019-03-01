from django.db.models.signals import pre_delete
from django.dispatch import receiver

from adhocracy4.projects.models import Project

from .emails import DeleteProjectEmail


@receiver(pre_delete, sender=Project)
def sendDeleteProjectNotification(sender, instance, **kwargs):
    DeleteProjectEmail.send_no_object(instance)
