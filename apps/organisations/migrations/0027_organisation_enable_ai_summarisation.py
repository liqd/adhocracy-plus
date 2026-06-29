from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("a4_candy_organisations", "0026_alter_organisation_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="enable_ai_summarisation",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "When enabled, projects of this organisation can use AI "
                    "summarisation on the project detail page."
                ),
                verbose_name="Enable AI summarisation",
            ),
        ),
    ]
