from email.utils import parseaddr

import pytest
from django.core import mail

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
