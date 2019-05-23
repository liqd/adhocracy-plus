# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils import timezone
import datetime


class Migration(migrations.Migration):

    replaces = [('meinberlin_offlineevents', '0002_require_date')]

    dependencies = [
        ('a4_candy_offlineevents', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offlineevent',
            name='date',
            field=models.DateTimeField(verbose_name='Date', default=timezone.make_aware(datetime.datetime(1970, 1, 1, 1, 0))),
            preserve_default=False,
        ),
    ]
