from django.db import migrations


def restore_hidden_settings(apps, schema_editor):
    """Re-enable categories that were silently disabled by the settings form.

    The notification settings form used to submit fields that were not
    rendered in the template. Missing checkboxes were saved as ``False``,
    which disabled these categories for every user who saved the form.
    """
    NotificationSettings = apps.get_model(
        "a4_candy_notifications", "NotificationSettings"
    )
    NotificationSettings.objects.update(
        email_messages=True,
        notify_messages=True,
        email_invitations=True,
        notify_invitations=True,
        email_moderation=True,
        notify_moderation=True,
        email_warnings=True,
        notify_warnings=True,
        track_project_updates=True,
        track_project_events=True,
        track_user_engagement=True,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("a4_candy_notifications", "0006_remove_notificationsettings_email_newsletter"),
    ]

    operations = [
        migrations.RunPython(restore_hidden_settings, migrations.RunPython.noop),
    ]
