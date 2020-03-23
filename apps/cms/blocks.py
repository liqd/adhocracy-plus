from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock


class CallToActionBlock(blocks.StructBlock):
    body = blocks.RichTextBlock(required=False)
    link = blocks.CharBlock(required=False)
    link_text = blocks.CharBlock(
        required=False, max_length=50, label='Link Text'
    )

    class Meta:
        template = 'a4_candy_cms_pages/blocks/cta_block.html'
        icon = 'plus-inverse'


class ImageCTABlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    body = blocks.RichTextBlock(required=False)
    link = blocks.CharBlock(required=False)
    link_text = blocks.CharBlock(
        required=False, max_length=50, label='Link Text'
    )

    class Meta:
        template = 'a4_candy_cms_pages/blocks/img_cta_block.html'
        icon = 'view'


# 2-col, headline, text, CTA btn, background colors, text colors
class ColBackgroundCTABlock(blocks.StructBlock):
    column1_bg = CallToActionBlock(label='CTA column light blue')
    column2_bg = CallToActionBlock(label='CTA column dark blue')

    class Meta:
        template = 'a4_candy_cms_pages/blocks/col_background_cta_block.html'
        icon = 'tick-inverse'


# 2-col, headline, text, CTA btn, image, list
class ColumnsImageCTABlock(blocks.StructBlock):
    column1_img = CallToActionBlock(label='CTA column')
    column2_img = ImageCTABlock(label='Wide image CTA column')

    class Meta:
        template = 'a4_candy_cms_pages/blocks/col_img_cta_block.html'
        icon = 'list-ul'


# 3 column block with an optional button/link for each col,
# Call-to-action block can have up to 3 big CTA btn
class ColumnsCTABlock(blocks.StructBlock):
    columns_count = blocks.ChoiceBlock(choices=[
        (1, 'One column'),
        (2, 'Two columns'),
        (3, 'Three columns')

    ], default=3)

    columns = blocks.ListBlock(
        CallToActionBlock(label='CTA Column')
    )

    class Meta:
        template = 'a4_candy_cms_pages/blocks/col_cta_block.html'
        icon = 'grip'


class DocsBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    body = blocks.RichTextBlock(required=False)

    class Meta:
        template = 'a4_candy_cms_pages/blocks/docs_block.html'
        icon = 'arrow-down'


class AccordeonBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    content = blocks.RichTextBlock()

    class Meta:
        template = 'a4_candy_cms_pages/blocks/accordeon_block.html'


class AccordeonListBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    entries = blocks.ListBlock(AccordeonBlock)

    class Meta:
        template = 'a4_candy_cms_pages/blocks/accordeon_list_block.html'


class DownloadBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    document = DocumentChooserBlock()
    document_type = blocks.CharBlock(required=False)

    class Meta:
        template = 'a4_candy_cms_pages/blocks/download_block.html'


class DownloadListBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    documents = blocks.ListBlock(DownloadBlock)

    class Meta:
        template = 'a4_candy_cms_pages/blocks/download_list_block.html'


class QuoteBlock(blocks.StructBlock):
    color = blocks.ChoiceBlock(choices=[
        ('turquoise', 'turquoise'),
        ('blue', 'dark blue')
    ], default=1)
    image = ImageChooserBlock()
    quote = blocks.TextBlock()
    quote_author = blocks.CharBlock(required=False)
    link = blocks.URLBlock(required=False)
    link_text = blocks.CharBlock(
        required=False, max_length=50, label='Link Text'
    )

    class Meta:
        template = 'a4_candy_cms_pages/blocks/quote_block.html'
