import django.db.models.deletion
from django.db import migrations
from django.db import models

# Permission levels that used to be hardcoded choices on LearningCategory.
DEFAULT_LEVELS = (
    ("teilnehmer:in", "Teilnehmer:in", 10),
    ("initiator:in", "Initiator:in", 20),
    ("moderator:in", "Moderator:in", 30),
)

# Values written by older migrations before the ":in" suffix was introduced.
LEGACY_ALIASES = {
    "participant": "teilnehmer:in",
    "teilnehmer": "teilnehmer:in",
    "initiator": "initiator:in",
    "moderator": "moderator:in",
}

REVERSE_LEVELS = {name: value for value, name, order in DEFAULT_LEVELS}


def forwards(apps, schema_editor):
    """Create the editable permission levels and keep existing categories."""
    LearningCategory = apps.get_model("a4_candy_learning_nuggets", "LearningCategory")
    PermissionLevel = apps.get_model("a4_candy_learning_nuggets", "PermissionLevel")

    levels = {}
    for value, name, order in DEFAULT_LEVELS:
        level, _ = PermissionLevel.objects.get_or_create(
            name=name,
            defaults={"order": order},
        )
        levels[value] = level

    stored_values = (
        LearningCategory.objects.exclude(permission_level__isnull=True)
        .exclude(permission_level="")
        .values_list("permission_level", flat=True)
        .distinct()
    )

    for value in stored_values:
        canonical = LEGACY_ALIASES.get(value, value)
        level = levels.get(canonical)
        if level is None:
            # Unknown legacy values are preserved as their own editable level
            # instead of silently dropping the category from the index.
            level, _ = PermissionLevel.objects.get_or_create(
                name=canonical,
                defaults={"order": 100},
            )
            levels[canonical] = level

        LearningCategory.objects.filter(permission_level=value).update(
            permission_level_new=level
        )


def backwards(apps, schema_editor):
    """Restore the string based permission level when rolling back."""
    LearningCategory = apps.get_model("a4_candy_learning_nuggets", "LearningCategory")
    PermissionLevel = apps.get_model("a4_candy_learning_nuggets", "PermissionLevel")

    for level in PermissionLevel.objects.all():
        LearningCategory.objects.filter(permission_level_new=level).update(
            permission_level=REVERSE_LEVELS.get(level.name, level.name[:50])
        )


class Migration(migrations.Migration):

    dependencies = [
        ("a4_candy_learning_nuggets", "0008_normalise_permission_level"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="PermissionLevel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=60, unique=True)),
                ("order", models.IntegerField(default=0)),
            ],
            options={
                "verbose_name": "Permission Level",
                "verbose_name_plural": "Permission Levels",
                "ordering": ["order", "name"],
            },
        ),
        migrations.AddField(
            model_name="learningcategory",
            name="permission_level_new",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="categories",
                to="a4_candy_learning_nuggets.permissionlevel",
            ),
        ),
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(
            model_name="learningcategory",
            name="permission_level",
        ),
        migrations.RenameField(
            model_name="learningcategory",
            old_name="permission_level_new",
            new_name="permission_level",
        ),
        migrations.AddField(
            model_name="learningnuggetpage",
            name="icon",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Upload a PNG icon for this nugget " "(recommended size: 24x24px)."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="learningnuggetpage",
            name="read_length",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Estimated reading time in minutes.",
                null=True,
            ),
        ),
    ]
