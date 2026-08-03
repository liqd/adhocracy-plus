import pytest
from django.core.management import call_command
from guest_user.models import Guest

from tests.helpers import GuestUserCreator


def make_converted_guest():
    """A guest who converted: real email and username, leftover Guest row."""
    guest = GuestUserCreator().create_guest_user()
    guest.email = "converted@example.com"
    guest.username = "converteduser"
    guest.save()
    return guest


@pytest.mark.django_db
def test_command_deletes_only_converted_guest_rows():
    real_guest = GuestUserCreator().create_guest_user()
    converted_guest = make_converted_guest()

    call_command("delete_converted_guest_rows")

    assert Guest.objects.filter(user=real_guest).exists()
    assert not Guest.objects.filter(user=converted_guest).exists()


@pytest.mark.django_db
def test_command_dry_run_deletes_nothing():
    converted_guest = make_converted_guest()

    call_command("delete_converted_guest_rows", dry_run=True)

    assert Guest.objects.filter(user=converted_guest).exists()
