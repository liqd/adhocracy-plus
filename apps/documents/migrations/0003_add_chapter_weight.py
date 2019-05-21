# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('meinberlin_documents', '0003_add_chapter_weight')]

    dependencies = [
        ('a4_candy_documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='weight',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
