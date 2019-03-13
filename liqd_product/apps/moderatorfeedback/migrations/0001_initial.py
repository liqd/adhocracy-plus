# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import ckeditor.fields
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('meinberlin_moderatorfeedback', '0001_initial')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ModeratorStatement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(blank=True, null=True, editable=False)),
                ('statement', ckeditor.fields.RichTextField(blank=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'db_table': 'meinberlin_moderatorfeedback_moderatorstatement',
            },
        ),
    ]
