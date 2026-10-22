import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_mark_notification_as_read_view(client, user_factory, notification_factory):
    # Create a user and log them in
    user = user_factory()
    client.force_login(user)

    # Create a notification for the user
    notification = notification_factory(recipient=user, read=False)

    # Call the mark as read view with a redirect URL
    redirect_url = "/some-safe-url/"
    url = (
        reverse("mark_notification_as_read", kwargs={"pk": notification.id})
        + f"?redirect_to={redirect_url}"
    )

    response = client.get(url)

    # Check that the notification was marked as read
    notification.refresh_from_db()
    assert notification.read is True
    assert response.status_code == 302
    assert response.url == redirect_url


@pytest.mark.django_db
def test_trigger_tasks_requires_staff(client, user, mocker):
    client.force_login(user)
    started = mocker.patch(
        "apps.notifications.views." "send_recently_started_project_notifications.delay"
    )

    response = client.post(reverse("trigger_all_notification_tasks"))

    assert response.status_code == 403
    started.assert_not_called()


@pytest.mark.django_db
def test_trigger_tasks_runs_globally_without_slug(client, admin, mocker):
    client.force_login(admin)
    started = mocker.patch(
        "apps.notifications.views." "send_recently_started_project_notifications.delay"
    )
    completed = mocker.patch(
        "apps.notifications.views."
        "send_recently_completed_project_notifications.delay"
    )
    events = mocker.patch(
        "apps.notifications.views.send_upcoming_event_notifications.delay"
    )

    response = client.post(reverse("trigger_all_notification_tasks"))

    assert response.status_code == 302
    started.assert_called_once_with(project_id=None)
    completed.assert_called_once_with(project_id=None)
    events.assert_called_once_with(project_id=None)


@pytest.mark.django_db
def test_trigger_tasks_scoped_to_project_slug(client, admin, project_factory, mocker):
    project = project_factory()
    client.force_login(admin)
    started = mocker.patch(
        "apps.notifications.views." "send_recently_started_project_notifications.delay"
    )
    completed = mocker.patch(
        "apps.notifications.views."
        "send_recently_completed_project_notifications.delay"
    )
    events = mocker.patch(
        "apps.notifications.views.send_upcoming_event_notifications.delay"
    )

    response = client.post(
        reverse("trigger_all_notification_tasks"),
        {"project_slug": project.slug},
    )

    assert response.status_code == 302
    started.assert_called_once_with(project_id=project.pk)
    completed.assert_called_once_with(project_id=project.pk)
    events.assert_called_once_with(project_id=project.pk)


@pytest.mark.django_db
def test_trigger_tasks_unknown_slug_shows_error(client, admin, mocker):
    client.force_login(admin)
    started = mocker.patch(
        "apps.notifications.views." "send_recently_started_project_notifications.delay"
    )

    response = client.post(
        reverse("trigger_all_notification_tasks"),
        {"project_slug": "does-not-exist"},
        follow=True,
    )

    assert response.status_code == 200
    assert "No project found" in response.content.decode()
    started.assert_not_called()
