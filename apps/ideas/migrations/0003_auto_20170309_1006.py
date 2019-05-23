# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('meinberlin_ideas', '0003_auto_20170309_1006')]

    dependencies = [
        ('a4_candy_ideas', '0002_idea_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='idea',
            options={'ordering': ['-created']},
        ),
    ]
