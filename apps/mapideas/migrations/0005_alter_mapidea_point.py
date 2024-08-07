# Generated by Django 4.2.13 on 2024-08-05 06:53

import adhocracy4.maps.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("a4_candy_mapideas", "0004_alter_mapidea_item_ptr_alter_mapidea_labels"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mapidea",
            name="point",
            field=adhocracy4.maps.fields.PointField(
                help_text="Click inside the marked area to set the marker. A set marker can be dragged when pressed.",
                verbose_name="Where can your idea be located on a map?",
            ),
        ),
    ]
