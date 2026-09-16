import django.db.models.deletion
from django.db import migrations, models
from django.db.models import F


def migrate_idea_fk_to_generic(apps, schema_editor):
    """Move answers from the old ``idea`` FK to the generic foreign key.

    All existing answers were attached to ``Idea`` instances, so their content
    type is always the concrete ``Idea`` model.
    """
    CustomFieldAnswer = apps.get_model("a4_candy_customfields", "CustomFieldAnswer")
    ContentType = apps.get_model("contenttypes", "ContentType")
    idea_content_type = ContentType.objects.get_for_model(
        apps.get_model("a4_candy_ideas", "Idea")
    )
    CustomFieldAnswer.objects.update(
        content_type=idea_content_type.pk, object_id=F("idea_id")
    )


class Migration(migrations.Migration):

    dependencies = [
        ("a4_candy_customfields", "0001_initial"),
        ("a4_candy_ideas", "0007_alter_idea_creator_contact_consent_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="customfieldanswer",
            name="unique_answer_per_idea_and_field",
        ),
        migrations.AddField(
            model_name="customfieldanswer",
            name="content_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="customfieldanswer",
            name="object_id",
            field=models.PositiveIntegerField(blank=True, null=True),
            preserve_default=False,
        ),
        # No reverse code: the migration is one-way. Rolling back would have
        # to re-add the non-null ``idea`` FK column, which cannot be restored
        # reliably from the generic foreign key.
        migrations.RunPython(migrate_idea_fk_to_generic),
        migrations.RemoveField(
            model_name="customfieldanswer",
            name="idea",
        ),
        migrations.AlterField(
            model_name="customfieldanswer",
            name="content_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="customfieldanswer",
            name="object_id",
            field=models.PositiveIntegerField(),
        ),
        migrations.AddConstraint(
            model_name="customfieldanswer",
            constraint=models.UniqueConstraint(
                fields=("content_type", "object_id", "field"),
                name="unique_answer_per_object_and_field",
            ),
        ),
    ]
