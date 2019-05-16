# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import liqd_product.apps.moderatorfeedback.fields


class Migration(migrations.Migration):

    replaces = [('meinberlin_budgeting', '0005_inherit_from_moderateable')]

    dependencies = [
        ('liqd_product_moderatorfeedback', '__first__'),
        ('liqd_product_budgeting', '0004_remove_moderator_statement_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='moderator_feedback',
            field=liqd_product.apps.moderatorfeedback.fields.ModeratorFeedbackField(null=True, choices=[('CONSIDERATION', 'Under consideration'), ('REJECTED', 'Rejected'), ('ACCEPTED', 'Accepted')], blank=True, default=None, max_length=254),
        ),
        migrations.AddField(
            model_name='proposal',
            name='moderator_statement',
            field=models.OneToOneField(null=True, related_name='+', to='liqd_product_moderatorfeedback.ModeratorStatement', on_delete=models.CASCADE),
        ),
    ]
