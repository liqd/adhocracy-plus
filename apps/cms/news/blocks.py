from wagtail.core import blocks


class NewsBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    news_page = blocks.PageChooserBlock(
        target_model='a4_candy_cms_news.NewsIndexPage')

    class Meta:
        template = 'a4_candy_cms_news/blocks/news_block.html'
        icon = 'grip'
