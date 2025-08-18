import logging

from django.conf import settings
from django.forms import widgets
from django.template import loader
from django.utils.translation import get_language

logger = logging.getLogger(__name__)


class ProsopoCaptchaWidget(widgets.HiddenInput):
    class Media:
        js = ("prosopo.js",)

    def render(self, name, value, attrs, renderer=None):
        site_key = getattr(settings, "PROSOPO_SITE_KEY", "")
        widget_id = attrs.get("id", f"id_{name}")

        logger.info(
            f"ProsopoCaptchaWidget: name={name}, id={widget_id}, site_key={site_key}"
        )

        context = {
            "name": name,
            "id": widget_id,
            "site_key": site_key,
            "LANGUAGE_CODE": get_language(),
        }

        return loader.render_to_string(
            "a4_candy_captcha/prosopo_captcha_widget.html", context
        )
