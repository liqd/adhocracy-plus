import pytest
from django.urls import reverse

from adhocracy4.projects.models import Project
from adhocracy4.test import helpers


@pytest.mark.django_db
def test_project_with_geojson_point(project_factory, geos_point):
    # Create a Project instance with the GisGeos point
    project = project_factory(is_app_accessible=True, point=geos_point)

    fetched_project = Project.objects.get(id=project.id)

    # Check if the point is correctly stored
    assert fetched_project.point.equals(geos_point)


@pytest.mark.django_db
def test_project_geojson_point_serialiser(
    user,
    project_factory,
    module_factory,
    organisation_factory,
    phase_factory,
    apiclient,
    geos_point,
    geojson_point,
):
    organisation = organisation_factory(enable_geolocation=True)
    project = project_factory(organisation=organisation, point=geos_point)
    module = module_factory(project=project)
    phase = phase_factory(module=module)

    url = reverse("app-projects-list")
    apiclient.login(username=user.email, password="password")
    with helpers.freeze_phase(phase):
        response = apiclient.get(url, format="json")

    assert response.status_code == 200
    assert response.data[0]["point"] == geojson_point
