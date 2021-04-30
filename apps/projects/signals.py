from django.db.models import signals
from django.dispatch import receiver

from adhocracy4.projects.models import Project

from . import emails


@receiver(signals.m2m_changed, sender=Project.participants.through)
def send_welcome_to_private_project_email(
        action, **kwargs):
    if action == 'post_add':
        project = kwargs.get('instance')
        participant_pks = list(kwargs.get('pk_set'))

        emails.WelcomeToPrivateProjectEmail.send(
            project, participant_pks=participant_pks)
