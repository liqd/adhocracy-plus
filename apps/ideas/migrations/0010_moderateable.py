# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-07 16:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import apps.moderatorfeedback.fields


class Migration(migrations.Migration):

    replaces = [('meinberlin_ideas', '0010_moderateable')]

    dependencies = [
        ('a4_candy_moderatorfeedback', '0001_initial'),
        ('a4_candy_ideas', '0009_remove_universal_phase'),
    ]

    operations = [
        migrations.AddField(
            model_name='idea',
            name='moderator_feedback',
            field=apps.moderatorfeedback.fields.ModeratorFeedbackField(blank=True, choices=[('CONSIDERATION', 'Under consideration'), ('REJECTED', 'Rejected'), ('ACCEPTED', 'Accepted')], default=None, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='idea',
            name='moderator_statement',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='a4_candy_moderatorfeedback.ModeratorStatement'),
        ),
    ]
