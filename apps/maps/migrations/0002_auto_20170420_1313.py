# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('meinberlin_maps', '0002_auto_20170420_1313')]

    dependencies = [
        ('a4_candy_maps', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mappreset',
            options={'ordering': ['name']},
        ),
    ]
