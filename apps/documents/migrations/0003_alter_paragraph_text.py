# Generated by Django 3.2.19 on 2024-02-29 11:03

import adhocracy4.images.validators
from django.db import migrations
import django_ckeditor_5.fields


class Migration(migrations.Migration):
    dependencies = [
        ("a4_candy_documents", "0002_verbose_name_created_modified"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paragraph",
            name="text",
            field=django_ckeditor_5.fields.CKEditor5Field(
                validators=[adhocracy4.images.validators.ImageAltTextValidator()]
            ),
        ),
    ]
