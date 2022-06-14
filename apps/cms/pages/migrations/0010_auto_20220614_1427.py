# Generated by Django 3.2.13 on 2022-06-14 12:27

import apps.cms.blocks
from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('a4_candy_cms_pages', '0009_limit_char_elements_hero_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='body_streamfield_de',
            field=wagtail.fields.StreamField([('col_list_image_cta_block', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='List and Image')))])), ('background_cta_block', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='CTA with Background')))])), ('columns_cta', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns'), (3, 'Three columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='CTA Column')))])), ('html', wagtail.blocks.RawHTMLBlock()), ('paragraph', wagtail.blocks.RichTextBlock()), ('news', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock()), ('news_page', wagtail.blocks.PageChooserBlock(page_type=['a4_candy_cms_news.NewsIndexPage']))])), ('use_cases', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock()), ('use_cases', wagtail.blocks.ListBlock(wagtail.blocks.PageChooserBlock(page_type=['a4_candy_cms_use_cases.UseCasePage']))), ('demo_platform', wagtail.blocks.URLBlock()), ('use_case_page', wagtail.blocks.PageChooserBlock(page_type=['a4_candy_cms_use_cases.UseCaseIndexPage']))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='body_streamfield_en',
            field=wagtail.fields.StreamField([('col_list_image_cta_block', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='List and Image')))])), ('background_cta_block', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='CTA with Background')))])), ('columns_cta', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns'), (3, 'Three columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='CTA Column')))])), ('html', wagtail.blocks.RawHTMLBlock()), ('paragraph', wagtail.blocks.RichTextBlock()), ('news', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock()), ('news_page', wagtail.blocks.PageChooserBlock(page_type=['a4_candy_cms_news.NewsIndexPage']))])), ('use_cases', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock()), ('use_cases', wagtail.blocks.ListBlock(wagtail.blocks.PageChooserBlock(page_type=['a4_candy_cms_use_cases.UseCasePage']))), ('demo_platform', wagtail.blocks.URLBlock()), ('use_case_page', wagtail.blocks.PageChooserBlock(page_type=['a4_candy_cms_use_cases.UseCaseIndexPage']))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='simplepage',
            name='body_streamfield_de',
            field=wagtail.fields.StreamField([('html', wagtail.blocks.RawHTMLBlock()), ('richtext', wagtail.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('faq', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('entries', wagtail.blocks.ListBlock(apps.cms.blocks.AccordeonBlock))])), ('image_cta', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))])), ('col_list_image_cta_block', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='List and Image')))])), ('columns_cta', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns'), (3, 'Three columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='CTA Column')))])), ('downloads', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('documents', wagtail.blocks.ListBlock(apps.cms.blocks.DownloadBlock))])), ('quote', wagtail.blocks.StructBlock([('color', wagtail.blocks.ChoiceBlock(choices=[('turquoise', 'turquoise'), ('blue', 'dark blue')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('quote', wagtail.blocks.TextBlock()), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))]))], use_json_field=True),
        ),
        migrations.AlterField(
            model_name='simplepage',
            name='body_streamfield_en',
            field=wagtail.fields.StreamField([('html', wagtail.blocks.RawHTMLBlock()), ('richtext', wagtail.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('faq', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('entries', wagtail.blocks.ListBlock(apps.cms.blocks.AccordeonBlock))])), ('image_cta', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))])), ('col_list_image_cta_block', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='List and Image')))])), ('columns_cta', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns'), (3, 'Three columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='CTA Column')))])), ('downloads', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('documents', wagtail.blocks.ListBlock(apps.cms.blocks.DownloadBlock))])), ('quote', wagtail.blocks.StructBlock([('color', wagtail.blocks.ChoiceBlock(choices=[('turquoise', 'turquoise'), ('blue', 'dark blue')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('quote', wagtail.blocks.TextBlock()), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='simplepage',
            name='body_streamfield_ky',
            field=wagtail.fields.StreamField([('html', wagtail.blocks.RawHTMLBlock()), ('richtext', wagtail.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('faq', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('entries', wagtail.blocks.ListBlock(apps.cms.blocks.AccordeonBlock))])), ('image_cta', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))])), ('col_list_image_cta_block', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='List and Image')))])), ('columns_cta', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns'), (3, 'Three columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='CTA Column')))])), ('downloads', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('documents', wagtail.blocks.ListBlock(apps.cms.blocks.DownloadBlock))])), ('quote', wagtail.blocks.StructBlock([('color', wagtail.blocks.ChoiceBlock(choices=[('turquoise', 'turquoise'), ('blue', 'dark blue')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('quote', wagtail.blocks.TextBlock()), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='simplepage',
            name='body_streamfield_nl',
            field=wagtail.fields.StreamField([('html', wagtail.blocks.RawHTMLBlock()), ('richtext', wagtail.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('faq', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('entries', wagtail.blocks.ListBlock(apps.cms.blocks.AccordeonBlock))])), ('image_cta', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))])), ('col_list_image_cta_block', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='List and Image')))])), ('columns_cta', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns'), (3, 'Three columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='CTA Column')))])), ('downloads', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('documents', wagtail.blocks.ListBlock(apps.cms.blocks.DownloadBlock))])), ('quote', wagtail.blocks.StructBlock([('color', wagtail.blocks.ChoiceBlock(choices=[('turquoise', 'turquoise'), ('blue', 'dark blue')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('quote', wagtail.blocks.TextBlock()), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='simplepage',
            name='body_streamfield_ru',
            field=wagtail.fields.StreamField([('html', wagtail.blocks.RawHTMLBlock()), ('richtext', wagtail.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('faq', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('entries', wagtail.blocks.ListBlock(apps.cms.blocks.AccordeonBlock))])), ('image_cta', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))])), ('col_list_image_cta_block', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='List and Image')))])), ('columns_cta', wagtail.blocks.StructBlock([('columns_count', wagtail.blocks.ChoiceBlock(choices=[(1, 'One column'), (2, 'Two columns'), (3, 'Three columns')])), ('columns', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('body', wagtail.blocks.RichTextBlock(required=False)), ('link', wagtail.blocks.CharBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))], label='CTA Column')))])), ('downloads', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('documents', wagtail.blocks.ListBlock(apps.cms.blocks.DownloadBlock))])), ('quote', wagtail.blocks.StructBlock([('color', wagtail.blocks.ChoiceBlock(choices=[('turquoise', 'turquoise'), ('blue', 'dark blue')])), ('image', wagtail.images.blocks.ImageChooserBlock()), ('quote', wagtail.blocks.TextBlock()), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(label='Link Text', max_length=50, required=False))]))], blank=True, use_json_field=True),
        ),
    ]
