import os
from datetime import timedelta

import pytest
from django.core import mail
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from apps.newsletters.emails import NewsletterSettingsNoticeEmail
from tests.helpers import GuestUserCreator


def log_lines(tmp_path):
    log_file = tmp_path / "notice.log"
    if not log_file.exists():
        return []
    return log_file.read_text().strip().splitlines()


@pytest.mark.django_db
def test_command_dry_run_sends_nothing(user_factory, tmp_path):
    log_file = tmp_path / "notice.log"
    user = user_factory(get_newsletters=False)
    user.last_login = timezone.now()
    user.save()

    call_command(
        "send_newsletter_settings_notice", dry_run=True, log_file=str(log_file)
    )

    assert len(mail.outbox) == 0
    assert not log_file.exists()


@pytest.mark.django_db
def test_command_sends_to_refined_candidate_pool(user_factory, tmp_path):
    log_file = tmp_path / "notice.log"
    affected = user_factory(get_newsletters=False)
    affected.last_login = timezone.now()
    affected.save()

    call_command("send_newsletter_settings_notice", log_file=str(log_file))

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [affected.email]
    assert "newsletter" in mail.outbox[0].subject.lower()
    lines = log_lines(tmp_path)
    assert len(lines) == 1
    assert lines[0].endswith(affected.email)


@pytest.mark.django_db
def test_command_excludes_non_candidates(user_factory, tmp_path):
    subscribed = user_factory(get_newsletters=True)
    subscribed.last_login = timezone.now()
    subscribed.save()

    inactive = user_factory(get_newsletters=False, is_active=False)
    inactive.last_login = timezone.now()
    inactive.save()

    not_logged_in_since = user_factory(get_newsletters=False)
    not_logged_in_since.last_login = timezone.now() - timedelta(days=400)
    not_logged_in_since.save()

    guest = GuestUserCreator().create_guest_user()
    guest.last_login = timezone.now()
    guest.save()

    call_command(
        "send_newsletter_settings_notice", log_file=str(tmp_path / "notice.log")
    )

    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_command_limit_limits_recipients(user_factory, tmp_path):
    log_file = tmp_path / "notice.log"
    for _ in range(3):
        user = user_factory(get_newsletters=False)
        user.last_login = timezone.now()
        user.save()

    call_command("send_newsletter_settings_notice", limit=1, log_file=str(log_file))

    assert len(mail.outbox) == 1
    assert len(log_lines(tmp_path)) == 1


@pytest.mark.django_db
def test_command_rerun_skips_already_notified(user_factory, tmp_path):
    log_file = tmp_path / "notice.log"
    affected = user_factory(get_newsletters=False)
    affected.last_login = timezone.now()
    affected.save()

    call_command("send_newsletter_settings_notice", log_file=str(log_file))
    call_command("send_newsletter_settings_notice", log_file=str(log_file))

    assert len(mail.outbox) == 1
    assert len(log_lines(tmp_path)) == 1


@pytest.mark.django_db
def test_command_to_sends_test_copy_without_logging(user_factory, tmp_path):
    log_file = tmp_path / "notice.log"
    user_factory(email="test@example.com")

    call_command(
        "send_newsletter_settings_notice", to="test@example.com", log_file=str(log_file)
    )

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["test@example.com"]
    assert not log_file.exists()


@override_settings(
    # Use the committed test catalog so the German rendering is deterministic
    # even in CI, where the real .mo files are not compiled.
    LOCALE_PATHS=[
        os.path.join(os.path.dirname(__file__), "locale"),
    ],
)
@pytest.mark.django_db
def test_email_renders_in_english_and_german(user_factory):
    user = user_factory()
    user.language = "de"
    user.save()

    mail.outbox.clear()
    NewsletterSettingsNoticeEmail(user).dispatch(user)

    assert len(mail.outbox) == 1
    subject = mail.outbox[0].subject
    assert "Neuigkeiten zu Ihren Newsletter-Einstellungen" in subject
    html = mail.outbox[0].alternatives[0][0]
    assert "Ihre Benachrichtigungs-Einstellungen" in html

    user.language = "en"
    user.save()
    mail.outbox.clear()
    NewsletterSettingsNoticeEmail(user).dispatch(user)

    assert len(mail.outbox) == 1
    assert "Update on your newsletter settings" in mail.outbox[0].subject
    html = mail.outbox[0].alternatives[0][0]
    assert "Your notification settings" in html
