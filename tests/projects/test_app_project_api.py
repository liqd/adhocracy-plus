import pytest
from django.urls import reverse

from adhocracy4.api.dates import get_date_display
from adhocracy4.test import helpers


@pytest.mark.django_db
def test_app_project_api(user, project_factory, apiclient):
    project_1 = project_factory(is_app_accessible=True)
    project_2 = project_factory(is_app_accessible=True)
    project_3 = project_factory(is_app_accessible=True)
    project_4 = project_factory(is_app_accessible=False)
    project_5 = project_factory(is_app_accessible=True, is_draft=True)
    project_6 = project_factory(is_app_accessible=True, is_archived=True)

    url = reverse("app-projects-list")
    response = apiclient.get(url, format="json")
    assert response.status_code == 401

    apiclient.login(username=user.email, password="password")
    response = apiclient.get(url, format="json")
    assert response.status_code == 200

    assert any(
        [
            True
            for dict in response.data
            if ("pk" in dict and dict["pk"] == project_1.pk)
        ]
    )
    assert any(
        [
            True
            for dict in response.data
            if ("pk" in dict and dict["pk"] == project_2.pk)
        ]
    )
    assert any(
        [
            True
            for dict in response.data
            if ("pk" in dict and dict["pk"] == project_3.pk)
        ]
    )
    assert not any(
        [
            True
            for dict in response.data
            if ("pk" in dict and dict["pk"] == project_4.pk)
        ]
    )
    assert not any(
        [
            True
            for dict in response.data
            if ("pk" in dict and dict["pk"] == project_5.pk)
        ]
    )
    assert not any(
        [
            True
            for dict in response.data
            if ("pk" in dict and dict["pk"] == project_6.pk)
        ]
    )


@pytest.mark.django_db
def test_app_project_api_single_idea_collection_module(
    user, client, apiclient, project_factory
):
    project = project_factory(is_app_accessible=True)
    organisation = project.organisation
    initiator = organisation.initiators.first()
    url = reverse(
        "a4dashboard:module-create",
        kwargs={
            "organisation_slug": organisation.slug,
            "project_slug": project.slug,
            "blueprint_slug": "idea-collection",
        },
    )
    client.login(username=initiator.email, password="password")
    response = client.post(url)
    assert project.modules.count() == 1
    module = project.modules[0]
    module.is_draft = False
    module.save()

    url = reverse("app-projects-list")
    apiclient.login(username=user.email, password="password")
    response = apiclient.get(url, format="json")

    assert response.status_code == 200
    assert response.data[0]["single_idea_collection_module"] == module.pk
    assert response.data[0]["single_poll_module"] is False


@pytest.mark.django_db
def test_app_project_api_single_poll_module(user, client, apiclient, project_factory):
    project = project_factory(is_app_accessible=True)
    organisation = project.organisation
    initiator = organisation.initiators.first()
    url = reverse(
        "a4dashboard:module-create",
        kwargs={
            "organisation_slug": organisation.slug,
            "project_slug": project.slug,
            "blueprint_slug": "poll",
        },
    )
    client.login(username=initiator.email, password="password")
    response = client.post(url)
    assert project.modules.count() == 1
    module = project.modules[0]
    module.is_draft = False
    module.save()

    url = reverse("app-projects-list")
    apiclient.login(username=user.email, password="password")
    response = apiclient.get(url, format="json")

    assert response.status_code == 200
    assert response.data[0]["single_idea_collection_module"] is False
    assert response.data[0]["single_poll_module"] == module.pk


@pytest.mark.django_db
def test_app_project_serializer(
    user, project_factory, module_factory, phase_factory, apiclient
):
    html_whitespace = "    <p>text with a <strong>bold</strong> bit</p>    "
    html_no_whitespace = "<p>text with a <strong>bold</strong> bit</p>"
    project = project_factory(
        is_app_accessible=True,
        information=html_whitespace,
        contact_name="Name Name",
        result=html_whitespace,
    )
    module = module_factory(project=project)
    module_factory(project=project, is_draft=True)
    phase = phase_factory(module=module)

    url = reverse("app-projects-list")
    apiclient.login(username=user.email, password="password")
    with helpers.freeze_phase(phase):
        response = apiclient.get(url, format="json")

    assert response.status_code == 200
    assert response.data[0]["information"] == html_no_whitespace
    assert response.data[0]["result"] == html_no_whitespace
    assert response.data[0]["published_modules"] == [module.pk]
    assert response.data[0]["organisation"] == project.organisation.name
    assert response.data[0]["access"] == "PUBLIC"
    assert response.data[0]["single_idea_collection_module"] is False
    assert response.data[0]["single_poll_module"] is False
    assert response.data[0]["participation_time_display"].endswith("remaining")
    assert response.data[0]["module_running_progress"] == 0
    assert response.data[0]["has_contact_info"] is True
    assert response.data[0]["contact_name"] == "Name Name"
    assert response.data[0]["contact_phone"] == ""

    with helpers.freeze_pre_phase(phase):
        response = apiclient.get(url, format="json")
    assert response.data[0][
        "participation_time_display"
    ] == "Participation: from " + get_date_display(phase.start_date)
    assert not response.data[0]["module_running_progress"]

    with helpers.freeze_post_phase(phase):
        response = apiclient.get(url, format="json")
    assert (
        response.data[0]["participation_time_display"]
        == "Participation ended. Read result."
    )
    assert not response.data[0]["module_running_progress"]
