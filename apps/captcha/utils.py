import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def verify_token(token):
    url = "https://api.prosopo.io/siteverify"

    if not token:
        logger.warning("Empty token provided for verification")
        return False

    secret_key = getattr(settings, "PROSOPO_SECRET_KEY", "")
    if not secret_key:
        logger.error("PROSOPO_SECRET_KEY not configured")
        return False

    data = {"secret": secret_key, "token": token}
    response = requests.post(url, json=data)
    return response.json().get(
        "verified", False
    )  # Return verified field, default to False
