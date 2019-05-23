# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('meinberlin_actions', '0002_delete_action')]

    dependencies = [
        ('a4_candy_actions', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Action',
        ),
    ]
