import pytest
from django.urls import reverse

from adhocracy4.projects.models import Project
from adhocracy4.test import helpers

# Define a GeoJSON point
geojson_point = {
    "type": "Feature",
    "properties": {},
    "geometry": {"type": "Point", "coordinates": [1.0, 1.0]},
}


@pytest.mark.django_db
def test_project_with_geojson_point(project_factory):
    project = project_factory(is_app_accessible=True)

    # Create a Project instance with the GeoJSON point
    project.point = geojson_point
    project.save()

    fetched_project = Project.objects.get(id=project.id)

    # Check if the point is correctly stored
    assert fetched_project.point == geojson_point
    assert fetched_project.point["geometry"]["coordinates"] == [
        1.0,
        1.0,
    ]  # Check coordinates


@pytest.mark.django_db
def test_project_geojson_point_serialiser(
    user,
    project_factory,
    module_factory,
    organisation_factory,
    phase_factory,
    apiclient,
):
    organisation = organisation_factory(enable_geolocation=True)
    project = project_factory(organisation=organisation, point=geojson_point)
    module = module_factory(project=project)
    phase = phase_factory(module=module)

    url = reverse("app-projects-list")
    apiclient.login(username=user.email, password="password")
    with helpers.freeze_phase(phase):
        response = apiclient.get(url, format="json")

    assert response.status_code == 200
    assert response.data[0]["point"] == str(geojson_point)
