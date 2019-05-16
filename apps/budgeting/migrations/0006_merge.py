# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('meinberlin_budgeting', '0006_merge')]

    dependencies = [
        ('liqd_product_budgeting', '0005_inherit_from_moderateable'),
        ('liqd_product_budgeting', '0004_use_explicit_item_ptr'),
    ]

    operations = [
    ]
