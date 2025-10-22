import pytest
from django.urls import reverse

from adhocracy4.test.helpers import redirect_target
from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_notify_on_project_created(client, organisation, user):
    """Check if initiator gets email on project create via dashboard."""
    initiator = organisation.initiators.first()
    organisation.initiators.add(user)
    url = reverse(
        "a4dashboard:project-create",
        kwargs={
            "organisation_slug": organisation.slug,
        },
    )

    data = {"name": "project name", "description": "project description", "access": 1}

    client.login(username=initiator, password="password")
    response = client.post(url, data)
    assert redirect_target(response) == "project-edit"

    initiator_emails = get_emails_for_address(initiator.email)
    assert len(initiator_emails) == 1
    assert initiator_emails[0].subject.startswith("New project project name")


@pytest.mark.django_db
def test_notify_on_project_deleted(client, project):
    """Check if initiator gets email on project delete."""
    organisation = project.organisation
    initiator = organisation.initiators.first()
    project.delete()

    initiator_emails = get_emails_for_address(initiator.email)
    assert len(initiator_emails) == 2
    assert initiator_emails[1].subject.startswith("Deletion of project")


# TODO: Check logic here
# @pytest.mark.django_db
# def test_notify_on_project_deleted_no_orga(client, project):
#     """Check no email or error when project is deleted with organisation."""
#     organisation = project.organisation
#     organisation.delete()

#     assert len(mail.outbox) == 0
