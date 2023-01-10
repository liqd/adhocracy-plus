from django import forms
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from adhocracy4.filters.widgets import OrderingWidget
from adhocracy4.images.widgets import ImageInputWidget


class Select2Mixin:
    def __init__(self, *args, **kwargs):
        if "attrs" not in kwargs:
            kwargs["attrs"] = {}
        if "class" not in kwargs["attrs"]:
            kwargs["attrs"]["class"] = ""
        kwargs["attrs"]["class"] += " js-select2"

        super().__init__(*args, **kwargs)

    class Media:
        js = ("select2.js",)


class Select2Widget(Select2Mixin, forms.Select):
    pass


class Select2MultipleWidget(Select2Mixin, forms.SelectMultiple):
    pass


class TextWithDatalistWidget(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        attrs = self.build_attrs(self.attrs, attrs)
        options = self.get_options(attrs.pop("options"))

        if "list" not in attrs:
            attrs["list"] = attrs["id"] + "_datalist"

        return render_to_string(
            "a4_candy_contrib/text_with_datalist.html",
            {
                "text_input": super().render(name, value, attrs, renderer),
                "id_for_datalist": attrs["list"],
                "options": options,
            },
        )

    def get_options(self, options):
        if callable(options):
            return options()
        if options:
            return options
        return {}


class AplusOrderingWidget(OrderingWidget):
    # FIXME: only because https://github.com/liqd/adhocracy-plus/issues/1659
    # test and remove from time to time
    label = _("Ordering")


class ImageInputWidgetSimple(ImageInputWidget):
    """Almost same as ImageInputWidget.

    Only difference is that it is not showing info box about image
    only being uploaded after clicking save.
    """

    widget_template_name = "a4images/image_upload_widget_simple.html"
