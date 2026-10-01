from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.blocks import CharBlock
from wagtail.blocks import RichTextBlock
from wagtail.blocks import StructBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageBlock


class CallToActionBlock(blocks.StructBlock):
    body = blocks.RichTextBlock(required=False)
    link = blocks.CharBlock(required=False)
    link_text = blocks.CharBlock(required=False, max_length=50, label="Link Text")

    class Meta:
        template = "a4_candy_cms_pages/blocks/cta_block.html"
        icon = "plus-inverse"


class ImageCTABlock(blocks.StructBlock):
    image = ImageBlock(required=False)
    body = blocks.RichTextBlock(required=False)
    link = blocks.CharBlock(required=False)
    link_text = blocks.CharBlock(required=False, max_length=50, label="Link Text")

    class Meta:
        template = "a4_candy_cms_pages/blocks/img_cta_block.html"
        icon = "view"


# 2-col, headline, text, CTA btn, background colors, text colors
class ColumnsImageCTABlock(blocks.StructBlock):
    columns_count = blocks.ChoiceBlock(
        choices=[(1, "One column"), (2, "Two columns")], default=2
    )

    columns = blocks.ListBlock(ImageCTABlock(label="List and Image"))

    class Meta:
        template = "a4_candy_cms_pages/blocks/col_img_cta_block.html"
        icon = "list-ul"


class ColBackgroundCTABlock(blocks.StructBlock):
    columns_count = blocks.ChoiceBlock(
        choices=[(1, "One column"), (2, "Two columns")], default=2
    )

    columns = blocks.ListBlock(CallToActionBlock(label="CTA with Background"))

    class Meta:
        template = "a4_candy_cms_pages/blocks/col_background_cta_block.html"
        icon = "tick-inverse"


# 3 column block with an optional button/link for each col,
# Call-to-action block can have up to 3 big CTA btn
class ColumnsCTABlock(blocks.StructBlock):
    columns_count = blocks.ChoiceBlock(
        choices=[(1, "One column"), (2, "Two columns"), (3, "Three columns")], default=3
    )

    columns = blocks.ListBlock(CallToActionBlock(label="CTA Column"))

    class Meta:
        template = "a4_candy_cms_pages/blocks/col_cta_block.html"
        icon = "grip"


class DocsBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    body = blocks.RichTextBlock(required=False)

    class Meta:
        template = "a4_candy_cms_pages/blocks/docs_block.html"
        icon = "arrow-down"


class AccordeonBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    content = blocks.RichTextBlock()

    class Meta:
        template = "a4_candy_cms_pages/blocks/accordeon_block.html"


class AccordeonListBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    entries = blocks.ListBlock(AccordeonBlock)

    class Meta:
        template = "a4_candy_cms_pages/blocks/accordeon_list_block.html"


class DownloadBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    document = DocumentChooserBlock()
    document_type = blocks.CharBlock(required=False)

    class Meta:
        template = "a4_candy_cms_pages/blocks/download_block.html"


class DownloadListBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    documents = blocks.ListBlock(DownloadBlock)

    class Meta:
        template = "a4_candy_cms_pages/blocks/download_list_block.html"


class QuoteBlock(blocks.StructBlock):
    color = blocks.ChoiceBlock(
        choices=[("turquoise", "turquoise"), ("blue", "dark blue")], default=1
    )
    image = ImageBlock()
    quote = blocks.TextBlock()
    quote_author = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)
    link_text = blocks.CharBlock(required=False, max_length=50, label="Link Text")

    class Meta:
        template = "a4_candy_cms_pages/blocks/quote_block.html"


class VideoBlock(StructBlock):
    title = CharBlock(max_length=130, required=False)
    description = CharBlock(
        max_length=500,
        required=False,
        help_text=_(
            "Please insert a short description of the video " "(character limit 500)."
        ),
    )
    media = DocumentChooserBlock(
        help_text=_(
            "Please upload or choose a media "
            "file with any of the following extensions: "
            "MP4, WebM, MP3, WAV"
        ),
        required=False,
    )
    transcript = RichTextBlock(
        features=["bold", "italic", "ol", "ul", "link", "document-link"],
        help_text=_(
            "You can add the video's " "transcript here (unlimited " "characters)."
        ),
        required=False,
    )

    class Meta:
        template = "a4_candy_cms_pages/blocks/video_block.html"
        icon = "media"
        label = "Video Block"
