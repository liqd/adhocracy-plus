import pytest

from apps.notifications.forms import NotificationSettingsForm
from apps.notifications.models import NotificationSettings


def settings_form_data(get_newsletters=False):
    """POST data for the notification settings form."""
    data = {
        "email_initiator_publish_results": "on",
        "email_project_updates": "on",
        "notify_project_updates": "on",
        "email_project_events": "on",
        "notify_project_events": "on",
        "email_user_engagement": "on",
        "notify_user_engagement": "on",
    }
    if get_newsletters:
        data["get_newsletters"] = "on"
    return data


@pytest.mark.django_db
def test_newsletter_toggle_turns_optin_on(user):
    settings = NotificationSettings.get_for_user(user)
    form = NotificationSettingsForm(
        instance=settings, data=settings_form_data(get_newsletters=True)
    )
    assert form.is_valid(), form.errors
    form.save()

    user.refresh_from_db()
    assert user.get_newsletters is True


@pytest.mark.django_db
def test_newsletter_toggle_turns_optin_off(user):
    user.get_newsletters = True
    user.save()
    settings = NotificationSettings.get_for_user(user)

    form = NotificationSettingsForm(
        instance=settings, data=settings_form_data(get_newsletters=False)
    )
    assert form.is_valid(), form.errors
    form.save()

    user.refresh_from_db()
    assert user.get_newsletters is False


@pytest.mark.django_db
def test_newsletter_toggle_initial_reflects_current_optin(user):
    user.get_newsletters = True
    user.save()
    settings = NotificationSettings.get_for_user(user)

    form = NotificationSettingsForm(instance=settings)
    assert form["get_newsletters"].initial is True


@pytest.mark.django_db
def test_saving_settings_keeps_hidden_preferences(user):
    """Saving the settings page must not reset preferences without a toggle.

    These fields are not rendered in the template, so they are not part of the
    submitted data and the form must leave their stored values untouched.
    """
    settings = NotificationSettings.get_for_user(user)
    settings.email_messages = False
    settings.notify_messages = False
    settings.email_invitations = False
    settings.notify_invitations = False
    settings.email_moderation = False
    settings.notify_moderation = False
    settings.email_warnings = False
    settings.notify_warnings = False
    settings.track_project_updates = False
    settings.track_project_events = False
    settings.track_user_engagement = False
    settings.save()

    form = NotificationSettingsForm(instance=settings, data=settings_form_data())
    assert form.is_valid(), form.errors
    form.save()

    settings.refresh_from_db()
    assert settings.email_messages is False
    assert settings.notify_messages is False
    assert settings.email_invitations is False
    assert settings.notify_invitations is False
    assert settings.email_moderation is False
    assert settings.notify_moderation is False
    assert settings.email_warnings is False
    assert settings.notify_warnings is False
    assert settings.track_project_updates is False
    assert settings.track_project_events is False
    assert settings.track_user_engagement is False
