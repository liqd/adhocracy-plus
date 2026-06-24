import pytest
from allauth.account.models import EmailAddress
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from adhocracy4.test.helpers import redirect_target
from apps.projects.models import ParticipantInvite
from tests.helpers import get_emails_for_address


@pytest.mark.django_db
def test_unregistered_user_visit_stashes_verified_email(client, participant_invite):
    url = participant_invite.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200
    assert client.session.get("account_verified_email") == participant_invite.email


@pytest.mark.django_db
@override_settings(CAPTCHA=False)
def test_signup_from_participant_invite_skips_email_verification(
    client, participant_invite, signup_url
):
    invite_url = participant_invite.get_absolute_url()
    client.get(invite_url)
    mail.outbox.clear()

    response = client.post(
        signup_url,
        {
            "username": "inviteduser",
            "email": participant_invite.email,
            "password1": "password",
            "password2": "password",
            "terms_of_use": "on",
            "next": invite_url,
        },
    )
    assert response.status_code == 302
    assert len(mail.outbox) == 0
    assert EmailAddress.objects.filter(
        email=participant_invite.email, verified=True
    ).exists()
    assert "_auth_user_id" in client.session


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
    assert redirect_target(response) == "landing_page"
    user_mails = get_emails_for_address(user.email)
    assert len(user_mails) == 0
    assert ParticipantInvite.objects.all().count() == 0
