from django import template
from wagtail.images.shortcuts import get_rendition_or_not_found

register = template.Library()


@register.simple_tag
def get_first_nugget_image(nugget, rendition_spec):
    """
    Gets the first image from a nugget's content StreamField
    """
    for block in nugget.specific.content:  # Make sure to use .specific
        if block.block_type == "learning_nugget":
            # Adjust this based on your actual block structure
            image = block.value.get("image") or block.value.get("thumbnail")
            if image:
                return get_rendition_or_not_found(image, rendition_spec)
    return None


@register.simple_tag
def get_permission(permission_level):
    permissions = {
        "participant": "a4_candy_learning_nuggets.view_participant_content",
        "initiator": "a4_candy_learning_nuggets.view_initiator_content",
        "moderator": "a4_candy_learning_nuggets.view_moderator_content",
    }
    return permissions.get(permission_level, "")


@register.simple_tag
def get_permission_display(value):
    return value[0].upper() + value[1:] if value else value


@register.filter(name="filter_by_block_type")
def filter_by_block_type(blocks, block_type):
    """Filters StreamField blocks by their block_type."""
    return [block for block in blocks if block.block_type == block_type and block.value]
