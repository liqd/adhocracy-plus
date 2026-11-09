from email.utils import parseaddr

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.urls import reverse
from rest_framework import status

from apps.account.emails import AccountDeletionEmail


@pytest.mark.django_db
def test_aplus_email_from_name_with_organisation(
    organisation_factory,
    project_factory,
    module_factory,
    idea_factory,
):
    organisation = organisation_factory(name="City Council")
    project = project_factory(organisation=organisation)
    module = module_factory(project=project)
    idea_factory(module=module)

    display_name, _ = parseaddr(mail.outbox[0].from_email)
    org_name, platform_name = display_name.split(" | ", 1)
    assert org_name == "City Council"
    assert platform_name


@pytest.mark.django_db
def test_aplus_email_from_name_without_organisation(user):
    AccountDeletionEmail.send(user)

    display_name, _ = parseaddr(mail.outbox[0].from_email)
    assert display_name
    assert " | " not in display_name


@pytest.mark.django_db
def test_report_moderator_email_is_sent(apiclient, user, user2, idea_factory):
    idea = idea_factory()
    idea.project.moderators.add(user2)
    apiclient.force_authenticate(user=user)
    content_type = ContentType.objects.get_for_model(idea)

    response = apiclient.post(
        reverse("reports-list"),
        {
            "content_type": content_type.pk,
            "object_pk": idea.pk,
            "description": "Test report",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert any("Moderation request" in message.subject for message in mail.outbox)


@pytest.mark.django_db
def test_aplus_email_attachment_valid_image(
    organisation_factory,
    project_factory,
    module_factory,
    idea_factory,
    small_image,
    test_file,
):
    """Check that organisation logo is correctly attached to email"""
    organisation = organisation_factory(logo=small_image)
    project = project_factory(organisation=organisation)
    module = module_factory(project=project)
    idea_factory(module=module)

    attachments = mail.outbox[0].attachments[0]
    assert "image/jpeg" in str(attachments)
    assert "image/text/plain" not in str(attachments)


@pytest.mark.django_db
def test_aplus_email_attachment_invalid_image(
    organisation_factory,
    project_factory,
    module_factory,
    idea_factory,
    test_file,
):
    """Check that organisation logo is correctly attached to email even if MIMEImage
    fails to detect the mime type"""
    organisation = organisation_factory(logo=test_file)
    project = project_factory(organisation=organisation)
    module = module_factory(project=project)
    idea_factory(module=module)

    attachments = mail.outbox[0].attachments[0]
    assert "image/jpeg" not in str(attachments)
    assert "image/text/plain" in str(attachments)
