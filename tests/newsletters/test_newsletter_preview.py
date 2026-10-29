import pytest
from django.core import mail
from django.urls import reverse

from adhocracy4.follows import models as follow_models
from apps.newsletters import models as newsletter_models


def preview_url(organisation):
    return reverse(
        "a4dashboard:newsletter-preview",
        kwargs={"organisation_slug": organisation.slug},
    )


def preview_send_url(organisation):
    return reverse(
        "a4dashboard:newsletter-preview-send",
        kwargs={"organisation_slug": organisation.slug},
    )


def newsletter_data(project, **overrides):
    data = {
        "sender_name": "Jane Doe",
        "sender": "jane@example.org",
        "subject": "Newsletter subject",
        "body": "<p>Hello <strong>world</strong></p>",
        "receivers": newsletter_models.PROJECT,
        "organisation": project.organisation.pk,
        "project": project.pk,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_newsletter_form_has_preview_and_test_send_actions(client, admin, project):
    client.login(username=admin.email, password="password")
    url = reverse(
        "a4dashboard:newsletter-create",
        kwargs={"organisation_slug": project.organisation.slug},
    )

    response = client.get(url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "js-newsletter-preview-trigger" in content
    assert "js-newsletter-test-send" in content
    assert "newsletter-preview-modal" in content
    assert "View Draft" in content
    assert 'hx-include="#newsletter-form"' in content
    assert "js-newsletter-test-status" in content
    assert "newsletter-preview__action" in content
    assert "js-newsletter-send" in content
    assert "newsletter-send" in content
    assert 'form="newsletter-form"' in content


@pytest.mark.django_db
def test_preview_requires_permission(client, project, user_factory):
    user = user_factory()
    client.login(username=user.email, password="password")

    response = client.post(preview_url(project.organisation), newsletter_data(project))

    assert response.status_code == 403


@pytest.mark.django_db
def test_preview_renders_email(client, admin, project):
    client.login(username=admin.email, password="password")

    response = client.post(preview_url(project.organisation), newsletter_data(project))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Newsletter subject" in content
    assert "<strong>world</strong>" in content
    assert project.organisation.name in content
    assert "cid:logo" not in content
    assert "images/email_logo.png" in content
    assert "Jane Doe &lt;jane@example.org&gt;" in content
    assert "example recipient" not in content
    assert "text-align: left;" in content
    assert "js-newsletter-send" in content
    assert "newsletter-send" in content
    assert "Back to editing" in content
    assert "Send test email" in content
    assert "Send newsletter" in content
    assert "<html" not in content


@pytest.mark.django_db
def test_preview_uses_unsaved_values_without_saving(client, admin, project):
    client.login(username=admin.email, password="password")

    response = client.post(
        preview_url(project.organisation),
        newsletter_data(project, body="<p>Unsaved preview body</p>"),
    )

    assert "Unsaved preview body" in response.content.decode()
    assert newsletter_models.Newsletter.objects.count() == 0


@pytest.mark.django_db
def test_preview_opens_links_in_new_tab(client, admin, project):
    client.login(username=admin.email, password="password")

    response = client.post(
        preview_url(project.organisation),
        newsletter_data(project, body='<p><a href="https://example.org">Link</a></p>'),
    )

    content = response.content.decode()
    assert 'href="https://example.org"' in content
    assert 'target="_blank"' in content
    assert 'rel="noopener noreferrer"' in content


@pytest.mark.django_db
def test_preview_sends_test_email_only_to_current_user(
    client, admin, project, user_factory
):
    follower = user_factory(get_newsletters=True)
    client.login(username=admin.email, password="password")
    mail.outbox = []

    response = client.post(
        preview_send_url(project.organisation), newsletter_data(project)
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert "Test email sent" in content
    assert 'data-autodismiss="true"' in content
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [admin.email]
    assert mail.outbox[0].subject == "[TEST] Newsletter subject"
    assert mail.outbox[0].reply_to == ["Jane Doe <jane@example.org>"]
    assert follower.email not in mail.outbox[0].to


@pytest.mark.django_db
def test_preview_send_does_not_duplicate_test_prefix(client, admin, project):
    client.login(username=admin.email, password="password")
    mail.outbox = []

    client.post(
        preview_send_url(project.organisation),
        newsletter_data(project, subject="[TEST] Already marked"),
    )

    assert mail.outbox[0].subject == "[TEST] Already marked"


@pytest.mark.django_db
def test_preview_send_requires_subject(client, admin, project):
    client.login(username=admin.email, password="password")
    mail.outbox = []

    response = client.post(
        preview_send_url(project.organisation),
        newsletter_data(project, subject=""),
    )

    assert "Please add a subject" in response.content.decode()
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_preview_preserves_soft_line_breaks(client, admin, project):
    client.login(username=admin.email, password="password")

    response = client.post(
        preview_url(project.organisation),
        newsletter_data(project, body="Line one<br>Line two"),
    )

    content = response.content.decode()
    assert "Line one<br" in content
    assert "Line two" in content


@pytest.mark.django_db
def test_preview_shows_recipient_count(
    client, admin, project, user_factory, follow_factory
):
    follower = user_factory(get_newsletters=True)
    follow_models.Follow.objects.all().delete()
    follow_factory(creator=follower, project=project)

    client.login(username=admin.email, password="password")
    response = client.post(preview_url(project.organisation), newsletter_data(project))

    content = response.content.decode()
    assert 'newsletter-preview__recipient-count">1<' in content
    assert "Recipients" in content
