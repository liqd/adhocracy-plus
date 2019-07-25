# Generated by Django 2.2.3 on 2019-07-25 09:04

import adhocracy4.images.fields
import ckeditor.fields
import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('a4_candy_organisations', '0003_rename_table_to_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='description',
            field=models.CharField(default='empty description', help_text='The description will be displayed on the landing page. max. 400 characters', max_length=400, verbose_name='Short description of your organisation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='organisation',
            name='image',
            field=adhocracy4.images.fields.ConfiguredImageField('heroimage', blank=True, help_prefix='The image will be shown as a decorative background image.', upload_to='organisations/backgrounds', verbose_name='Header image'),
        ),
        migrations.AddField(
            model_name='organisation',
            name='imprint',
            field=ckeditor.fields.RichTextField(default='empty imprint', help_text='Please provide all the legally required information of your imprint. The imprint will be shown on a separate page.', verbose_name='Imprint'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='organisation',
            name='information',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, help_text='You can provide general information about your participation platform to your visitors. It’s also helpful to name a general person of contact for inquiries. The information will be shown on a separate page that can be reached via the main menu.', verbose_name='Information about your organisation'),
        ),
        migrations.AddField(
            model_name='organisation',
            name='logo',
            field=adhocracy4.images.fields.ConfiguredImageField('logo', blank=True, help_text='The Logo representing your organisation. The image must be square and it should be min. 200 pixels wide and 200 pixels tall. Allowed file formats are png, jpeg, gif. The file size should be max. 5 MB.', upload_to='organisations/logos', verbose_name='Logo'),
        ),
        migrations.AddField(
            model_name='organisation',
            name='slogan',
            field=models.CharField(blank=True, help_text='The slogan will be shown below the title of your organisation on the landing page. The slogan can provide context or additional information to the title. max. 200 characters', max_length=200, verbose_name='Slogan'),
        ),
        migrations.AddField(
            model_name='organisation',
            name='title',
            field=models.CharField(default='Organisation', help_text='The title of your organisation will be shown on the landing page. max. 100 characters', max_length=100, verbose_name='Title of your organisation'),
        ),
    ]
