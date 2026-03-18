import pytest
from django.core.files.base import ContentFile
from django.test.utils import override_settings

from apps.newsletters.emails import NewsletterEmail
from tests.factories import OrganisationFactory
from tests.factories import UserFactory
from tests.newsletters.factories import NewsletterFactory


@pytest.mark.django_db
def test_newsletter_email_has_no_default_greeting():
    """Newsletter emails should not render the default email_base greeting."""
    user = UserFactory()
    newsletter = NewsletterFactory(subject="Newsletter Subject", body="Body text")

    email = NewsletterEmail()
    email.object = newsletter
    email.kwargs = {
        "organisation": newsletter.project.organisation,
        "participant_ids": [user.id],
    }

    context = email.get_context()
    context["receiver"] = user

    _, _, html = email.render(email.template_name, context)
    assert "Hello" not in html
    assert "Guten Tag" not in html


@pytest.mark.django_db
def test_newsletter_email_uses_organisation_logo_as_inline_logo(tmp_path):
    """If an organisation logo exists, attach it as cid:logo."""
    with override_settings(MEDIA_ROOT=str(tmp_path)):
        organisation = OrganisationFactory()
        organisation.logo.save(
            "logo.png",
            ContentFile(b"fake-image-content"),
            save=True,
        )

        newsletter = NewsletterFactory(project=organisation.projects.first())
        user = UserFactory()

        email = NewsletterEmail()
        email.object = newsletter
        email.kwargs = {
            "organisation": organisation,
            "participant_ids": [user.id],
        }

        attachments = email.get_attachments()
        content_ids = [attachment["Content-Id"] for attachment in attachments]
        assert content_ids.count("<logo>") == 1
