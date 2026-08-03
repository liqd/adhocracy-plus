import pytest
from django.urls import reverse
from guest_user.functions import is_guest_user
from guest_user.models import Guest

from tests.helpers import GuestUserCreator


@pytest.mark.django_db
def test_guest_convert_deletes_guest_row(client):
    guest = GuestUserCreator().create_guest_user()
    client.force_login(guest)

    response = client.post(
        reverse("guest_convert"),
        {
            "email": "converted@example.com",
            "username": "converteduser",
            "password1": "testpassword123",
            "password2": "testpassword123",
            "terms_of_use": "on",
        },
    )

    assert response.status_code == 302
    guest.refresh_from_db()
    assert not Guest.objects.filter(user=guest).exists()
    assert not is_guest_user(guest)
