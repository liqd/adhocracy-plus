# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('meinberlin_documents', '0006_update_weight_field')]

    dependencies = [
        ('a4_candy_documents', '0005_update_content_types'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chapter',
            options={'ordering': ('weight',)},
        ),
        migrations.AlterField(
            model_name='chapter',
            name='weight',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
