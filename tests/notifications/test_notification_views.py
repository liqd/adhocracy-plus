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
