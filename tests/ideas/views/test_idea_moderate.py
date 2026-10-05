import pytest
from django.urls import reverse

from adhocracy4.test.factories import PhaseFactory
from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import setup_phase
from adhocracy4.test.helpers import setup_users
from apps.ideas import phases
from tests.ideas.factories import IdeaFactory


def setup_idea_moderation():
    phase, module, project, item = setup_phase(
        PhaseFactory, IdeaFactory, phases.FeedbackPhase
    )
    anonymous, moderator, initiator = setup_users(project)
    with freeze_phase(phase):
        url = reverse(
            "a4_candy_ideas:idea-moderate",
            kwargs={
                "organisation_slug": item.project.organisation.slug,
                "pk": item.pk,
                "year": item.created.year,
            },
        )
        detail_url = reverse(
            "userdashboard-moderation-detail", kwargs={"slug": project.slug}
        )
        return moderator, item, url, detail_url


@pytest.mark.django_db
def test_return_url_is_passed_to_context(client):
    moderator, item, url, detail_url = setup_idea_moderation()
    assert client.login(username=moderator.email, password="password")

    resp = client.get(url, {"next": detail_url})

    assert resp.status_code == 200
    assert resp.context["return_url"] == detail_url
    assert 'name="next" value="{}"'.format(detail_url) in resp.content.decode()


@pytest.mark.django_db
def test_external_return_url_is_rejected(client):
    moderator, item, url, detail_url = setup_idea_moderation()
    assert client.login(username=moderator.email, password="password")

    resp = client.get(url, {"next": "https://evil.example.com/"})

    assert resp.status_code == 200
    assert resp.context["return_url"] == ""


@pytest.mark.django_db
def test_next_is_used_as_success_url(client):
    moderator, item, url, detail_url = setup_idea_moderation()
    assert client.login(username=moderator.email, password="password")

    resp = client.post(
        url,
        {
            "moderateable-moderator_status": "ACCEPTED",
            "feedback_text-feedback_text": "Great idea",
            "next": detail_url,
        },
    )

    assert resp.status_code == 302
    assert resp.url == detail_url
