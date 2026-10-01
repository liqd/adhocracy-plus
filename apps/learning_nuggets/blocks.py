from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageBlock

from apps.cms.blocks import VideoBlock


class LearningExtrasBlock(blocks.StreamBlock):
    image = ImageBlock(
        required=False,
        help_text=_(
            "Upload an image that visually captures the content "
            "(recommended size: 600x400px, 3:2 ratio)"
        ),
    )
    video = VideoBlock(
        required=False,
        help_text=_(
            "Upload or select an instructional video to complement the written content "
            "(MP4 format recommended - 20mb)"
        ),
    )
    document = DocumentChooserBlock(
        required=False,
        help_text=_(
            "Upload related documents such as worksheets, guides, "
            "or additional resources (PDF format recommended)"
        ),
    )

    class Meta:
        label = "Media & Resources"
        icon = "placeholder"
        help_text = "Add optional media or documents as needed."


class LearningContentBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        required=True,
        max_length=100,
        help_text=_(
            "Enter a clear, concise title for this learning nugget "
            "(max 100 characters recommended)"
        ),
    )
    description = blocks.RichTextBlock(
        required=False,
        help_text=_(
            "Provide a comprehensive description of the learning nugget, "
            "including key takeaways and learning objectives"
        ),
    )
    thumbnail = ImageBlock(
        required=False,
        help_text=_(
            "Upload a representative image that visually captures the content "
            "(recommended size: 600x400px, 3:2 ratio)"
        ),
    )
    extras = LearningExtrasBlock(
        required=False,
        label="Extras",
        help_text=_("Choose optional content: videos, images, or documents."),
    )

    class Meta:
        template = "a4_candy_learning_nuggets/blocks/learning_content_block.html"
        icon = "media"
        label = "Learning Nugget Content"
