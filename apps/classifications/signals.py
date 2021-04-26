import logging

import backoff
import httpx
from django.conf import settings
from django.db.models import signals
from django.dispatch import receiver

from adhocracy4.comments.models import Comment

from .models import AIClassification

client = httpx.Client()
logger = logging.getLogger(__name__)


@receiver(signals.post_save, sender=Comment)
def get_ai_classification(sender, instance, **kwargs):
    if hasattr(settings, 'AI_USAGE') and settings.AI_USAGE:
        if hasattr(settings, 'AI_API_AUTH_TOKEN') and \
                settings.AI_API_AUTH_TOKEN:
            try:
                response = call_ai_api(comment=instance)
                if response.status_code == 200 \
                        and response.json()['classification'] == 'OFFENSE':

                    classification = AIClassification(
                        comment=instance,
                        classification='OFFENSIVE')
                    classification.save()
            except httpx.HTTPError as e:
                logger.error('Error connecting to %s: %s',
                             settings.AI_API_URL, str(e))
        else:
            logger.error('No ai api auth token provided. '
                         'Disable ai usage or provide token.')


def skip_retry(e):
    if isinstance(e, httpx.HTTPStatusError):
        return 400 <= e.response.status_code < 500
    return False


@backoff.on_exception(backoff.expo,
                      httpx.HTTPError,
                      max_tries=4,
                      factor=2,
                      giveup=skip_retry)
def call_ai_api(comment):
    response = client.post(settings.AI_API_URL,
                           data={'comment': comment.comment},
                           headers={'Authorization': 'Token {}'.format(
                                    settings.AI_API_AUTH_TOKEN),
                                    'Accept': 'application/json; version=2.0'})
    response.raise_for_status()

    return response
