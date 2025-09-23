from django.db import migrations
from django.contrib.auth import get_user_model


def create_notification_settings_for_existing_users(apps, schema_editor):
    User = get_user_model()
    NotificationSettings = apps.get_model(
        "a4_candy_notifications", "NotificationSettings"
    )

    # Get users that don't have notification settings yet
    users_without_settings = User.objects.filter(notification_settings__isnull=True)

    # Create settings using user IDs to avoid instance issues
    for user in users_without_settings:
        try:
            # Create directly without using the user instance in filter
            NotificationSettings.objects.create(user_id=user.id)
        except Exception as e:
            print(f"Skipping user {user.username} (ID: {user.id}) due to error: {e}")
            continue


def remove_notification_settings(apps, schema_editor):
    NotificationSettings = apps.get_model(
        "a4_candy_notifications", "NotificationSettings"
    )
    NotificationSettings.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("a4_candy_notifications", "0003_remove_notification_message_and_more"),
    ]

    operations = [
        migrations.RunPython(
            create_notification_settings_for_existing_users,
            remove_notification_settings,
        ),
    ]
