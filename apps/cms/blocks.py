from wagtail.core import blocks
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
    call_to_action = CallToActionBlock(required=False)

    class Meta:
        template = 'a4_candy_cms_pages/blocks/img_cta_block.html'
        icon = 'view'


# 2-col, headline, text, CTA btn, background colors, text colors
class ColumnsImageCTABlock(blocks.StructBlock):
    columns_count = blocks.ChoiceBlock(choices=[
        (1, 'One column'),
        (2, 'Two columns')

    ], default=2)

    columns = blocks.ListBlock(
        ImageCTABlock(label='CTA Img Column body')
    )

    class Meta:
        template = 'a4_candy_cms_pages/blocks/col_img_cta_block.html'
        icon = 'plus-inverse'


class ColBackgroundCTABlock(blocks.StructBlock):
    columns_count = blocks.ChoiceBlock(choices=[
        (1, 'One column'),
        (2, 'Two columns')

    ], default=2)

    columns = blocks.ListBlock(
        CallToActionBlock(label='CTA Background Column body')
    )

    class Meta:
        template = 'a4_candy_cms_pages/blocks/col_background_cta_block.html'
        icon = 'plus-inverse'


# 3 column block with an optional button/link for each col,
# Call-to-action block can have up to 3 big CTA btn
class ColumnsCTABlock(blocks.StructBlock):
    columns_count = blocks.ChoiceBlock(choices=[
        (1, 'One column'),
        (2, 'Two columns'),
        (3, 'Three columns')

    ], default=3)

    columns = blocks.ListBlock(
        CallToActionBlock(label='CTA Column body')
    )

    class Meta:
        template = 'a4_candy_cms_pages/blocks/col_cta_block.html'
        icon = 'plus-inverse'


class DocsBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    body = blocks.RichTextBlock(required=False)

    class Meta:
        template = 'a4_candy_cms_pages/blocks/docs_block.html'
        icon = 'arrow-down'
