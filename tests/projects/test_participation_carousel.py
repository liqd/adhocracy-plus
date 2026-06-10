import pytest
from dateutil.parser import parse
from django.urls import reverse
from freezegun import freeze_time

from apps.projects.participation_carousel import legacy_initial_slide_redirect
from apps.projects.participation_carousel import participation_carousel_slide_url
from tests.offlineevents.factories import OfflineEventFactory


@pytest.mark.django_db
def test_participation_carousel_slide_url_for_module(
    project, module_factory, phase_factory
):
    module = module_factory(project=project)
    phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )
    date = project.participation_dates[0]
    assert participation_carousel_slide_url(project, date) == module.get_absolute_url()


@pytest.mark.django_db
def test_participation_carousel_slide_url_for_event(project):
    event = OfflineEventFactory(
        project=project,
        date=parse("2013-03-01 12:00:00 UTC"),
    )
    date = next(
        entry
        for entry in project.participation_dates
        if entry.get("slug") == event.slug
    )
    assert participation_carousel_slide_url(project, date) == event.get_absolute_url()


@pytest.mark.django_db
def test_legacy_initial_slide_redirect_invalid_index(
    project, module_factory, phase_factory
):
    module = module_factory(project=project)
    phase_factory(
        module=module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )
    assert legacy_initial_slide_redirect(project, "99") is None


@pytest.mark.django_db
def test_future_module_detail_sets_carousel_initial_slide(
    client, project, module_factory, phase_factory
):
    past_module = module_factory(project=project, weight=1)
    future_module = module_factory(project=project, weight=2)
    phase_factory(
        module=past_module,
        start_date=parse("2013-01-01 17:00:00 UTC"),
        end_date=parse("2013-01-01 19:00:00 UTC"),
    )
    phase_factory(
        module=future_module,
        start_date=parse("2013-02-01 17:00:00 UTC"),
        end_date=parse("2013-02-01 19:00:00 UTC"),
    )
    url = reverse(
        "module-detail",
        kwargs={
            "organisation_slug": project.organisation.slug,
            "module_slug": future_module.slug,
        },
    )

    with freeze_time(parse("2013-01-15 12:00:00 UTC")):
        response = client.get(url)

    assert response.status_code == 200
    assert response.context_data["initial_slide"] == future_module.get_timeline_index
    assert response.context_data["initial_slide"] == 1
