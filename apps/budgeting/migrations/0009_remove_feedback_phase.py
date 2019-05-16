# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from adhocracy4.phases.models import Phase


def _remove_feedback_phase(apps, schema_editor):
    Phase.objects.filter(
        type='meinberlin_budgeting:040:feedback'
    ).delete()


class Migration(migrations.Migration):

    replaces = [('meinberlin_budgeting', '0009_remove_feedback_phase')]

    dependencies = [
        ('a4_candy_budgeting', '0008_auto_20170529_1302'),
        ('a4phases', '0006_remove_weight_from_phase_type'),
    ]

    operations = [
        migrations.RunPython(_remove_feedback_phase)
    ]
