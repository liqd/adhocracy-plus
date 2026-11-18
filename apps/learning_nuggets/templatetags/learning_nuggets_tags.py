from django import template
from wagtail.images.shortcuts import get_rendition_or_not_found

register = template.Library()


@register.simple_tag
def get_first_nugget_image(nugget, rendition_spec):
    """Gets the first thumbnail from a nugget's content StreamField."""
    for block in nugget.specific.content:
        if block.block_type == "learning_nugget":
            image = block.value.get("thumbnail")
            if image:
                return get_rendition_or_not_found(image, rendition_spec)
    return None


@register.simple_tag
def get_permission_display(value):
    return value[0].upper() + value[1:] if value else value


@register.filter(name="filter_by_block_type")
def filter_by_block_type(blocks, block_type):
    """Filters StreamField blocks by their block_type."""
    return [block for block in blocks if block.block_type == block_type and block.value]
