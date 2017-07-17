# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a4projects', '0008_project_tile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalProject',
            fields=[
                ('project_ptr', models.OneToOneField(auto_created=True, to='a4projects.Project', primary_key=True, serialize=False, parent_link=True)),
                ('url', models.URLField()),
            ],
            options={
                'abstract': False,
            },
            bases=('a4projects.project',),
        ),
    ]
