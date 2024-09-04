# Generated by Django 4.2.13 on 2024-09-04 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("a4_candy_organisations", "0023_auto_20240328_1138"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="enable_geolocation",
            field=models.BooleanField(
                default=False,
                verbose_name="enable geolocation for projects",
            ),
        ),
    ]
