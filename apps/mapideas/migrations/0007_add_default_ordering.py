# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('meinberlin_mapideas', '0007_add_default_ordering')]

    dependencies = [
        ('a4_candy_mapideas', '0006_auto_20170529_1302'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mapidea',
            options={'ordering': ['-created']},
        ),
    ]
