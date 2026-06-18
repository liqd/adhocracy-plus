import pytest
from dateutil.parser import parse
from django.urls import reverse
from freezegun import freeze_time

from adhocracy4.follows.models import Follow
from adhocracy4.polls import phases
from adhocracy4.test.helpers import assert_template_response
from tests.offlineevents.factories import OfflineEventFactory


def project_detail_url(project):
    return reverse(
        "project-detail",
        kwargs={
            "slug": project.slug,
            "organisation_slug": project.organisation.slug,
        },
    )


@pytest.fixture
def project_detail_overview(project, module_factory, phase_factory):
    """Project detail overview with multiple published modules."""
    future_start = parse("2013-02-01 17:00:00 UTC")
    future_end = parse("2013-02-01 19:00:00 UTC")

    def add_module_with_phase():
        module = module_factory(project=project)
        phase_factory(module=module, start_date=future_start, end_date=future_end)
        return module

    while project.published_modules.count() < 2:
        add_module_with_phase()

    for module in project.published_modules.all():
        if not module.phase_set.exists():
            phase_factory(
                module=module,
                start_date=future_start,
                end_date=future_end,
            )
    return project


@pytest.mark.django_db
def test_project_detail_sidebar_running_status(
    client, project_detail_overview, phase_factory
):
    active_start = parse("2013-01-01 17:00:00 UTC")
    active_end = parse("2013-01-01 19:00:00 UTC")
    for module in project_detail_overview.published_modules.all():
        module.phase_set.all().delete()
        phase_factory(
            module=module,
            start_date=active_start,
            end_date=active_end,
        )
    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        response = client.get(project_detail_url(project_detail_overview))
    assert response.status_code == 200
    assert_template_response(response, "a4_candy_projects/project_detail.html")
    assert b"project-detail__sidebar" in response.content
    assert b"project-detail__status-dot--running" in response.content


@pytest.mark.django_db
def test_project_detail_sidebar_shows_event_and_module_counts(
    client, project_detail_overview
):
    OfflineEventFactory(project=project_detail_overview)

    response = client.get(project_detail_url(project_detail_overview))
    content = response.content
    assert b"2 Modules" in content or b"2 Module" in content
    assert b"1 Event" in content


@pytest.mark.django_db
def test_project_detail_followers_hidden_for_anonymous_without_followers(
    client, project_detail_overview
):
    Follow.objects.filter(project=project_detail_overview).delete()
    response = client.get(project_detail_url(project_detail_overview))
    assert b"project-detail__followers" not in response.content


@pytest.mark.django_db
def test_project_detail_static_follower_avatars_for_anonymous(
    client, project_detail_overview, follow_factory, user_factory
):
    follow_factory(
        project=project_detail_overview,
        creator=user_factory(),
        enabled=True,
    )
    response = client.get(project_detail_url(project_detail_overview))
    assert b"project-detail__followers" in response.content
    assert b"project-detail__avatars" in response.content
    assert b'data-a4-widget="project-detail-follow"' not in response.content


@pytest.mark.django_db
def test_project_detail_anonymous_follow_login_link(client, project_detail_overview):
    response = client.get(project_detail_url(project_detail_overview))
    assert b"project-detail-follow-actions" in response.content
    assert b"account_login" in response.content or b"/login" in response.content
    assert b'data-a4-widget="project-detail-follow"' not in response.content


@pytest.mark.django_db
def test_project_detail_authenticated_follow_widget(
    client, user, project_detail_overview
):
    client.force_login(user)
    response = client.get(project_detail_url(project_detail_overview))
    assert b'data-a4-widget="project-detail-follow"' in response.content
    assert b"project-detail-follow-actions" in response.content
    assert b"project-detail-followers-avatars" in response.content
    assert b"project-detail-followers-label" in response.content
    assert b"project-detail__followers" in response.content


@pytest.mark.django_db
def test_project_detail_authenticated_follow_widget_includes_follower(
    client, user, project_detail_overview, follow_factory, user_factory
):
    Follow.objects.filter(project=project_detail_overview).delete()
    follower = user_factory()
    follow_factory(
        project=project_detail_overview,
        creator=follower,
        enabled=True,
    )
    client.force_login(user)
    response = client.get(project_detail_url(project_detail_overview))
    assert b'data-a4-widget="project-detail-follow"' in response.content
    assert str(follower.pk).encode() in response.content


@pytest.mark.django_db
def test_project_detail_single_module_shows_overview(
    client, project, module_factory, phase_factory, poll_factory
):
    """Project URL always shows the overview, not inline phase content."""
    module = module_factory(project=project)
    poll_factory(module=module)
    phase_factory(
        module=module,
        phase_content=phases.VotingPhase(),
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )

    with freeze_time(parse("2013-01-01 18:00:00 UTC")):
        response = client.get(project_detail_url(project))

    assert response.status_code == 200
    assert_template_response(response, "a4_candy_projects/project_detail.html")
    assert response.context_data.get("module") is None
    assert b"project-detail__participation" in response.content
    assert b"project-detail__module-grid" in response.content


@pytest.mark.django_db
def test_project_detail_online_participation_section(client, project_detail_overview):
    module = project_detail_overview.published_modules.first()
    module.name = "Survey module"
    module.save()
    response = client.get(project_detail_url(project_detail_overview))
    assert b"project-detail__participation" in response.content
    assert b"Online participation" in response.content
    assert b"project-detail__module-grid" in response.content
    assert b"data-participation-view-btn" in response.content
    assert b"Survey module" in response.content


@pytest.mark.django_db
def test_project_detail_offline_event_on_page(client, project_detail_overview):
    """With a timeline, the current event tile shows event detail (not the events list)."""
    event = OfflineEventFactory(
        project=project_detail_overview,
        name="Town hall",
        date=parse("2010-01-01 12:00:00 UTC"),
    )
    response = client.get(project_detail_url(project_detail_overview))
    assert response.status_code == 200
    assert event.name.encode() in response.content
    assert b"1 Event" in response.content


@pytest.mark.django_db
def test_project_detail_insights_section(
    client,
    project_detail_overview,
    poll_factory,
    phase_factory,
    project_insight_factory,
):
    module = project_detail_overview.published_modules.first()
    module.blueprint_type = "PO"
    module.save()
    poll_factory(module=module)
    module.phase_set.all().delete()
    phase_factory(
        module=module,
        phase_content=phases.VotingPhase(),
        start_date=parse("2013-02-01 17:00:00 UTC"),
        end_date=parse("2013-02-01 19:00:00 UTC"),
    )
    project_insight_factory(project=project_detail_overview, display=True)

    response = client.get(project_detail_url(project_detail_overview))
    assert b"project-detail__insights" in response.content
    assert b"Results" in response.content
    assert b"Statistics &amp; Results" not in response.content


@pytest.mark.django_db
def test_project_detail_guest_alert_visible_for_anonymous(
    client, project_detail_overview
):
    response = client.get(project_detail_url(project_detail_overview))
    assert response.status_code == 200
    assert b"data-guest-alert" in response.content
    assert b"project-detail__guest-alert" in response.content


@pytest.mark.django_db
def test_project_detail_guest_alert_hidden_for_authenticated_user(
    client, project_detail_overview, user
):
    client.force_login(user)
    response = client.get(project_detail_url(project_detail_overview))
    assert response.status_code == 200
    assert b"data-guest-alert" not in response.content
