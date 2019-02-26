# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('meinberlin_documents', '0002_rename_document_to_chapter')]

    dependencies = [
        ('liqd_product_documents', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Document',
            new_name='Chapter',
        ),
        migrations.RenameField(
            model_name='paragraph',
            old_name='document',
            new_name='chapter',
        ),
        migrations.AlterModelTable(
            name='chapter',
            table='meinberlin_documents_chapter',
        ),
    ]
