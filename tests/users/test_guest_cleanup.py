from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from guest_user.functions import get_guest_model

from tests.helpers import GuestUserCreator

User = get_user_model()


def _make_guest_expired(guest, days=20):
    guest_model = get_guest_model()
    guest_model.objects.filter(user=guest).update(
        created_at=timezone.now() - timedelta(days=days)
    )


@pytest.mark.django_db
def test_cleanup_deletes_old_empty_guest():
    guest = GuestUserCreator().create_guest_user()
    _make_guest_expired(guest)

    call_command("delete_expired_guests")

    assert not User.objects.filter(pk=guest.pk).exists()


@pytest.mark.django_db
def test_cleanup_keeps_recent_empty_guest():
    guest = GuestUserCreator().create_guest_user()

    call_command("delete_expired_guests")

    assert User.objects.filter(pk=guest.pk).exists()


@pytest.mark.django_db
def test_cleanup_keeps_old_guest_with_contribution(module_factory):
    from tests.ideas.factories import IdeaFactory

    guest = GuestUserCreator().create_guest_user()
    _make_guest_expired(guest)
    IdeaFactory(module=module_factory(), creator=guest)

    call_command("delete_expired_guests")

    assert User.objects.filter(pk=guest.pk).exists()


@pytest.mark.django_db
def test_cleanup_dry_run_deletes_nothing():
    guest = GuestUserCreator().create_guest_user()
    _make_guest_expired(guest)

    call_command("delete_expired_guests", "--dry-run")

    assert User.objects.filter(pk=guest.pk).exists()
