# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import liqd_product.apps.moderatorfeedback.fields


class Migration(migrations.Migration):

    replaces = [('meinberlin_budgeting', '0002_proposal_moderator_feedback')]

    dependencies = [
        ('liqd_product_budgeting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='moderator_feedback',
            field=liqd_product.apps.moderatorfeedback.fields.ModeratorFeedbackField(choices=[('CONSIDERATION', 'Under consideration'), ('REJECTED', 'Rejected'), ('ACCEPTED', 'Accepted')]),
        ),
    ]
