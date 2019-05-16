# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('meinberlin_ideas', '0004_remove_category_related_name')]

    dependencies = [
        ('liqd_product_ideas', '0003_auto_20170309_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idea',
            name='category',
            field=models.ForeignKey(blank=True, related_name='+', on_delete=django.db.models.deletion.SET_NULL, null=True, to='a4categories.Category'),
        ),
    ]
