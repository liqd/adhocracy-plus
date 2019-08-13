from wagtail.core import blocks

from apps.cms.blocks import CallToActionBlock


class UseCaseBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    use_cases = blocks.ListBlock(blocks.PageChooserBlock(
        target_model='a4_candy_cms_use_cases.UseCasePage'))
    demo_platform = blocks.URLBlock()
    use_case_page = blocks.PageChooserBlock(
        target_model='a4_candy_cms_use_cases.UseCaseIndexPage')

    class Meta:
        template = 'a4_candy_cms_use_cases/blocks/use_cases_block.html'
        icon = 'grip'


class ExampleBlock(blocks.StructBlock):
    examples = blocks.ListBlock(
        CallToActionBlock(label='CTA Column')
    )

    class Meta:
        template = 'a4_candy_cms_use_cases/blocks/examples_block.html'
        icon = 'grip'
