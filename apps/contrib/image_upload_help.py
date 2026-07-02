from django.utils.translation import gettext_lazy as _


def image_upload_help_text(min_width, min_height):
    return _(
        "Allowed file formats are png, jpeg, and gif. "
        "Images are cropped and resized automatically when you upload them. "
        "For best results, use an image at least {min_width} pixels wide and "
        "{min_height} pixels tall."
    ).format(min_width=min_width, min_height=min_height)


IMAGE_UPLOAD_HERO_HELP_TEXT = image_upload_help_text(1500, 500)

IMAGE_UPLOAD_TILE_HELP_TEXT = image_upload_help_text(500, 300)

IMAGE_UPLOAD_IDEA_HELP_TEXT = image_upload_help_text(600, 400)

IMAGE_UPLOAD_LOGO_HELP_TEXT = _(
    "The image must be square. Allowed file formats are png, jpeg, and gif. "
    "Images are cropped and resized automatically when you upload them. "
    "For best results, use an image at least 200 pixels wide and 200 pixels "
    "tall."
)
