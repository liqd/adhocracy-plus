# Generated by Django 3.2.20 on 2023-11-09 07:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunSQL(
            sql=[
                "DROP TABLE IF EXISTS background_task",
                "DROP TABLE IF EXISTS background_task_completedtask",
            ],
            reverse_sql=migrations.RunSQL.noop,
        )
    ]