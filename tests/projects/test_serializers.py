import pytest
from dateutil.parser import parse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from freezegun import freeze_time

from adhocracy4.projects.models import Project
from apps.projects.serializers import ModerationProjectSerializer


@pytest.mark.django_db
def test_project_serializer(
    client,
    project_factory,
    phase_factory,
    ImagePNG,
):
    project_active = project_factory(
        name="active",
        image=ImagePNG,
        image_copyright="copyright",
        image_alt_text="img_alt",
    )
    project_future = project_factory(name="future")
    project_active_and_future = project_factory(name="active and future")
    project_past = project_factory(
        name="past",
        tile_image=ImagePNG,
        tile_image_copyright="copyright",
        tile_image_alt_text="img_alt",
    )

    now = parse("2013-01-01 18:00:00+01:00")
    yesterday = now - timezone.timedelta(days=1)
    last_week = now - timezone.timedelta(days=7)
    tomorrow = now + timezone.timedelta(days=1)
    next_week = now + timezone.timedelta(days=7)

    # active phase
    phase_factory(
        start_date=last_week,
        end_date=next_week,
        module__project=project_active,
    )

    # future phase
    phase_factory(
        start_date=tomorrow,
        end_date=next_week,
        module__project=project_future,
    )

    # active phase
    phase_factory(
        start_date=yesterday,
        end_date=tomorrow,
        module__project=project_active_and_future,
    )

    # future_phase
    phase_factory(
        start_date=tomorrow,
        end_date=next_week,
        module__project=project_active_and_future,
    )

    # past phase
    phase_factory(
        start_date=last_week,
        end_date=yesterday,
        module__project=project_past,
    )

    with freeze_time(now):
        projects = Project.objects.all().order_by("created")

        project_serializer = ModerationProjectSerializer(projects, many=True)
        project_data = project_serializer.data
        assert len(project_data) == 4

        assert project_data[0]["title"] == "active"
        assert project_data[1]["title"] == "future"
        assert project_data[2]["title"] == "active and future"
        assert project_data[3]["title"] == "past"

        assert project_data[0]["participation_string"] == _("running")

        assert project_data[2]["participation_string"] == _("running")
        assert project_data[3]["participation_string"] == _("completed")

        assert project_data[0]["active_phase"][0] == 50
        assert "7" in project_data[0]["active_phase"][1]
        assert not project_data[1]["active_phase"]
        assert project_data[2]["active_phase"][0] == 50
        assert "1" in project_data[2]["active_phase"][1]
        assert not project_data[3]["active_phase"]

        assert not project_data[0]["future_phase"]
        assert not project_data[3]["future_phase"]

        assert not project_data[0]["past_phase"]
        assert not project_data[1]["past_phase"]
        assert not project_data[2]["past_phase"]

        assert project_data[0]["participation_active"]
        assert project_data[1]["participation_active"]
        assert project_data[2]["participation_active"]
        assert not project_data[3]["participation_active"]

        assert project_data[0]["tile_image"]
        assert not project_data[1]["tile_image"]
        assert not project_data[2]["tile_image"]
        assert project_data[3]["tile_image"]

        assert project_data[0]["tile_image_copyright"]
        assert not project_data[1]["tile_image_copyright"]
        assert not project_data[2]["tile_image_copyright"]
        assert project_data[3]["tile_image_copyright"]

        assert not project_data[0]["tile_image_alt_text"]
        assert not project_data[1]["tile_image_alt_text"]
        assert not project_data[2]["tile_image_alt_text"]
        assert project_data[3]["tile_image_alt_text"]
