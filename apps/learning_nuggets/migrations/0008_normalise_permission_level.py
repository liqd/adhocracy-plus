from django.db import migrations

# Earlier migrations (0005/0006) stored the permission level without the ":in"
# suffix (and 0001 with the English "participant" key). Normalise any such rows
# to the values used by the current model so categories are not dropped from the
# Learning Center index.
FORWARD = {
    "participant": "teilnehmer:in",
    "teilnehmer": "teilnehmer:in",
    "initiator": "initiator:in",
    "moderator": "moderator:in",
}

REVERSE = {
    "teilnehmer:in": "teilnehmer",
    "initiator:in": "initiator",
    "moderator:in": "moderator",
}


def _update_levels(LearningCategory, mapping):
    for old, new in mapping.items():
        LearningCategory.objects.filter(permission_level=old).update(
            permission_level=new
        )


def normalise_permission_levels(apps, schema_editor):
    LearningCategory = apps.get_model("a4_candy_learning_nuggets", "LearningCategory")
    _update_levels(LearningCategory, FORWARD)


def denormalise_permission_levels(apps, schema_editor):
    LearningCategory = apps.get_model("a4_candy_learning_nuggets", "LearningCategory")
    _update_levels(LearningCategory, REVERSE)


class Migration(migrations.Migration):

    dependencies = [
        ("a4_candy_learning_nuggets", "0007_alter_learningcategory_permission_level"),
    ]

    operations = [
        migrations.RunPython(
            normalise_permission_levels, denormalise_permission_levels
        ),
    ]
