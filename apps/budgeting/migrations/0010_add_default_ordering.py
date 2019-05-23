# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('meinberlin_budgeting', '0010_add_default_ordering')]

    dependencies = [
        ('a4_candy_budgeting', '0009_remove_feedback_phase'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proposal',
            options={'ordering': ['-created']},
        ),
    ]
