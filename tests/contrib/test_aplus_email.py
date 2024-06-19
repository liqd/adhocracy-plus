import pytest
from django.core import mail


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

    assert len(mail.outbox) == 1
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

    assert len(mail.outbox) == 1
    attachments = mail.outbox[0].attachments[0]
    assert "image/jpeg" not in str(attachments)
    assert "image/text/plain" in str(attachments)
