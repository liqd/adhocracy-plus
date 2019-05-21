# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('meinberlin_mapideas', '0004_use_explicit_item_ptr')]

    dependencies = [
        ('a4_candy_mapideas', '0003_remove_category_related_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mapidea',
            name='item_ptr',
            field=models.OneToOneField(to='a4modules.Item', serialize=False, primary_key=True, related_name='a4_candy_mapideas_mapidea', parent_link=True, on_delete=models.CASCADE),
        ),
    ]
