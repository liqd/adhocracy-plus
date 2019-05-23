# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('meinberlin_polls', '0002_auto_20170503_1524')]

    dependencies = [
        ('a4_candy_polls', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([]),
        ),
    ]
