import pytest
from django.test import override_settings
from django.urls import reverse

from adhocracy4.polls import phases
from adhocracy4.test.helpers import setup_phase


@pytest.mark.django_db
@override_settings(
    CAPTCHA=True, PROSOPO_SITE_KEY="test-site-key", PROSOPO_SECRET_KEY="x"
)
def test_poll_detail_shows_captcha_for_unregistered_users(
    client, phase_factory, poll_factory
):
    """
    Regression test: the poll detail page for a module should render
    the Prosopo captcha widget when unregistered users are allowed.
    """
    phase, module, project, _ = setup_phase(
        phase_factory, poll_factory, phases.VotingPhase
    )

    # Seite wie im Browser des Users aufrufen:
    # /<organisation_slug>/projects/module/poll/
    url = reverse(
        "module-detail",
        kwargs={
            "organisation_slug": project.organisation.slug,
            "module_slug": module.slug,
        },
    )

    response = client.get(url)

    # Seite rendert Poll-Detail-Template
    assert "a4polls/poll_detail.html" in response.template_name

    # Captcha ist in Polls ein React-Widget: wir prüfen serverseitig, ob die
    # Prosopo-Konfiguration (SiteKey) an das Widget übergeben wird.
    content = response.content.decode("utf-8")
    assert 'data-a4-widget="polls"' in content
    assert "prosopoSiteKey" in content
    assert "test-site-key" in content
