# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('meinberlin_polls', '0003_choice_order')]

    dependencies = [
        ('a4_candy_polls', '0002_auto_20170503_1524'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='choice',
            options={'ordering': ['id']},
        ),
    ]
