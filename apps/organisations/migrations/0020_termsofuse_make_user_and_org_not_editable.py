# Generated by Django 3.2.13 on 2022-06-10 07:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('a4_candy_organisations', '0019_organisationtermsofuse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisationtermsofuse',
            name='organisation',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.A4_ORGANISATIONS_MODEL),
        ),
        migrations.AlterField(
            model_name='organisationtermsofuse',
            name='user',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]