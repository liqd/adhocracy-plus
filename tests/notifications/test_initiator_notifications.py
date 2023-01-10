import pytest
from django.core import mail
from django.urls import reverse

from adhocracy4.test.helpers import redirect_target


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

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to[0] == user.email
    assert mail.outbox[0].subject.startswith("New project project name")


@pytest.mark.django_db
def test_notify_on_project_deleted(client, project):
    """Check if initiator gets email on project delete."""
    organisation = project.organisation
    initiator = organisation.initiators.first()
    project.delete()

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to[0] == initiator.email
    assert mail.outbox[0].subject.startswith("Deletion of project")


@pytest.mark.django_db
def test_notify_on_project_deleted_no_orga(client, project):
    """Check no email or error when project is deleted with organisation."""
    organisation = project.organisation
    organisation.delete()

    assert len(mail.outbox) == 0
