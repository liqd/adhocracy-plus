# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import adhocracy4.images.fields


class Migration(migrations.Migration):

    replaces = [('liqd_product_users', '0002_add-user-fields-for-profile')]

    dependencies = [
        ('a4_candy_users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=adhocracy4.images.fields.ConfiguredImageField('avatar', verbose_name='Avatar picture', upload_to='users/images', blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.CharField(verbose_name='Biography', blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='facebook_handle',
            field=models.CharField(verbose_name='Facebook name', blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='user',
            name='homepage',
            field=models.CharField(verbose_name='Homepage', blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='user',
            name='twitter_handle',
            field=models.CharField(verbose_name='Twitter name', blank=True, max_length=15),
        ),
    ]
