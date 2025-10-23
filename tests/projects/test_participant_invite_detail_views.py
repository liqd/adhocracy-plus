import pytest
from django.urls import reverse

from adhocracy4.test.helpers import redirect_target
from apps.projects.models import ParticipantInvite
from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_user_can_accept(client, participant_invite, user):
    url = participant_invite.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200
    assert (
        response.template_name[0] == "a4_candy_projects/participantinvite_detail.html"
    )

    client.login(username=user.email, password="password")
    response = client.get(url)
    assert response.status_code == 302
    assert redirect_target(response) == "project-participant-invite-update"
    assert ParticipantInvite.objects.all().count() == 1
    assert str(
        ParticipantInvite.objects.first()
    ) == "Participation invite to {} for {}".format(
        participant_invite.project, participant_invite.email
    )

    data = {"accept": ""}

    organisation_slug = participant_invite.project.organisation.slug
    url = reverse(
        "project-participant-invite-update",
        kwargs={
            "organisation_slug": organisation_slug,
            "invite_token": participant_invite.token,
        },
    )

    response = client.post(url, data)
    assert response.status_code == 302
    assert redirect_target(response) == "project-detail"
    user_mails = get_emails_for_address(user.email)
    assert len(user_mails) == 1
    assert ParticipantInvite.objects.all().count() == 0


@pytest.mark.django_db
def test_user_can_reject(client, participant_invite, user):
    client.login(username=user.email, password="password")
    data = {"reject": ""}

    organisation_slug = participant_invite.project.organisation.slug
    url = reverse(
        "project-participant-invite-update",
        kwargs={
            "organisation_slug": organisation_slug,
            "invite_token": participant_invite.token,
        },
    )

    response = client.post(url, data)
    assert response.status_code == 302
    assert redirect_target(response) == "wagtail_serve"
    user_mails = get_emails_for_address(user.email)
    assert len(user_mails) == 0
    assert ParticipantInvite.objects.all().count() == 0
