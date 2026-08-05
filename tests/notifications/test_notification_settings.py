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
        "email_messages": "on",
        "notify_messages": "on",
        "email_invitations": "on",
        "notify_invitations": "on",
        "email_moderation": "on",
        "notify_moderation": "on",
        "email_warnings": "on",
        "notify_warnings": "on",
        "track_project_updates": "on",
        "track_project_events": "on",
        "track_user_engagement": "on",
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
