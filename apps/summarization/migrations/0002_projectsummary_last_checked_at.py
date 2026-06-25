from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("a4_candy_summarization", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectsummary",
            name="last_checked_at",
            field=models.DateTimeField(
                null=True,
                blank=True,
                verbose_name="Last Checked At",
                help_text=(
                    "Last time this summary was confirmed to match the project export."
                ),
            ),
        ),
    ]

