# Generated by Django 2.2.4 on 2019-08-08 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a4_candy_cms_news', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newsindexpage',
            name='demo_link',
        ),
        migrations.AlterField(
            model_name='newspage',
            name='teaser_de',
            field=models.TextField(blank=True, max_length=400, null=True, verbose_name='Teaser Text'),
        ),
        migrations.AlterField(
            model_name='newspage',
            name='teaser_en',
            field=models.TextField(blank=True, max_length=400, null=True, verbose_name='Teaser Text'),
        ),
    ]
