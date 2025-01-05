import pytest
from django.urls import reverse

from adhocracy4.api.dates import get_date_display
from adhocracy4.projects.enums import Access
from adhocracy4.test import helpers


@pytest.mark.django_db
def test_app_project_api(
    user,
    module_factory,
    organisation_factory,
    phase_factory,
    project_factory,
    apiclient,
):
    url = reverse("app-projects-list")

    organisation = organisation_factory(enable_geolocation=True)
    # Project factory by default has access assigned to Public
    project_1 = project_factory(organisation=organisation)
    project_2 = project_factory(access=Access.SEMIPUBLIC, organisation=organisation)
    project_3 = project_factory(
        access=Access.PUBLIC, is_draft=True, organisation=organisation
    )
    project_4 = project_factory(
        access=Access.PUBLIC, is_archived=True, organisation=organisation
    )
    project_5 = project_factory(access=Access.PRIVATE, organisation=organisation)

    module_1 = module_factory(project=project_1)
    module_2 = module_factory(project=project_2)
    module_3 = module_factory(project=project_3)
    module_4 = module_factory(project=project_4)
    module_5 = module_factory(project=project_5)

    phase_factory(module=module_1)
    phase_factory(module=module_2)
    phase_factory(module=module_3)
    phase_factory(module=module_4)
    phase = phase_factory(module=module_5)

    with helpers.freeze_phase(phase):
        response = apiclient.get(url, format="json")
    assert response.status_code == 401

    apiclient.login(username=user.email, password="password")
    with helpers.freeze_phase(phase):
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
    assert not any(
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


@pytest.mark.django_db
def test_app_project_api_not_show_past_projects(
    user,
    module_factory,
    organisation_factory,
    phase_factory,
    project_factory,
    apiclient,
):
    organisation = organisation_factory(enable_geolocation=True)
    # Project factory by default has access assigned to Public
    project_1 = project_factory(organisation=organisation)
    project_2 = project_factory(access=Access.SEMIPUBLIC, organisation=organisation)

    module = module_factory(project=project_1)
    phase = phase_factory(module=module)

    module = module_factory(project=project_2)
    phase = phase_factory(module=module)

    url = reverse("app-projects-list")
    apiclient.login(username=user.email, password="password")
    response = apiclient.get(url, format="json")
    assert response.status_code == 200

    with helpers.freeze_phase(phase):
        response = apiclient.get(url, format="json")
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
    with helpers.freeze_post_phase(phase):
        response = apiclient.get(url, format="json")

    assert not any(
        [
            True
            for dict in response.data
            if ("pk" in dict and dict["pk"] == project_1.pk)
        ]
    )
    assert not any(
        [
            True
            for dict in response.data
            if ("pk" in dict and dict["pk"] == project_2.pk)
        ]
    )

    with helpers.freeze_pre_phase(phase):
        response = apiclient.get(url, format="json")

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


@pytest.mark.django_db
def test_app_project_api_single_idea_collection_module(
    user, client, apiclient, organisation_factory, phase_factory, project_factory
):
    organisation = organisation_factory(enable_geolocation=True)
    # Project factory by default has access assigned to Public
    project = project_factory(organisation=organisation)
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
    phase = phase_factory(module=module)

    url = reverse("app-projects-list")
    with helpers.freeze_phase(phase):
        apiclient.login(username=user.email, password="password")
        response = apiclient.get(url, format="json")

    assert response.status_code == 200
    assert response.data[0]["single_idea_collection_module"] == module.pk
    assert response.data[0]["single_poll_module"] is False


@pytest.mark.django_db
def test_app_project_api_single_poll_module(
    user, client, apiclient, organisation_factory, phase_factory, project_factory
):
    organisation = organisation_factory(enable_geolocation=True)

    # Project factory by default has access assigned to Public
    project = project_factory(organisation=organisation)
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
    phase = phase_factory(module=module)

    url = reverse("app-projects-list")
    with helpers.freeze_phase(phase):
        apiclient.login(username=user.email, password="password")
        response = apiclient.get(url, format="json")

    assert response.status_code == 200
    assert response.data[0]["single_idea_collection_module"] is False
    assert response.data[0]["single_poll_module"] == module.pk


@pytest.mark.django_db
def test_app_project_serializer(
    user,
    project_factory,
    module_factory,
    organisation_factory,
    phase_factory,
    apiclient,
):
    organisation = organisation_factory(enable_geolocation=True)

    html_whitespace = "    <p>text with a <strong>bold</strong> bit</p>    "
    html_no_whitespace = "<p>text with a <strong>bold</strong> bit</p>"

    # Project factory by default has access assigned to Public
    project = project_factory(
        organisation=organisation,
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
    assert response.data[0]["url"]
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
    # Future projects are not shown in the projects list
    assert response.data[0][
        "participation_time_display"
    ] == "Participation: from " + get_date_display(phase.start_date)
    assert not response.data[0]["module_running_progress"]

    with helpers.freeze_post_phase(phase):
        response = apiclient.get(url, format="json")
    # Past projects are not shown in the projects list
    assert response.data == []


@pytest.mark.django_db
def test_app_project_api_with_jwt_auth(
    user,
    module_factory,
    organisation_factory,
    phase_factory,
    project_factory,
    apiclient,
):
    organisation = organisation_factory(enable_geolocation=True)

    # Project factory by default has access assigned to Public
    project_1 = project_factory(organisation=organisation)
    project_2 = project_factory(organisation=organisation)

    module_1 = module_factory(project=project_1)
    module_2 = module_factory(project=project_2)
    phase_factory(module=module_1)
    phase = phase_factory(module=module_2)

    url = reverse("app-projects-list")

    with helpers.freeze_phase(phase):
        response = apiclient.get(url, format="json")
    assert response.status_code == 401

    # Perform the login request
    login_data = {
        "username": user.email,
        "password": "password",
    }

    with helpers.freeze_phase(phase):
        response = apiclient.post(
            reverse("token_obtain_jwt"), login_data, format="json"
        )
        access_token = response.data["access"]
        apiclient.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
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


@pytest.mark.django_db
def test_retrieve_project_with_jwt_auth(
    apiclient,
    user,
    module_factory,
    organisation_factory,
    phase_factory,
    project_factory,
):
    organisation = organisation_factory(enable_geolocation=True)

    # Project factory by default has access assigned to Public
    project = project_factory(organisation=organisation)
    module = module_factory(project=project)
    phase = phase_factory(module=module)
    url = reverse("app-projects-detail", args=[project.slug])

    with helpers.freeze_phase(phase):
        response = apiclient.get(url)
    assert response.status_code == 401

    # Perform the login request
    login_data = {
        "username": user.email,
        "password": "password",
    }

    with helpers.freeze_phase(phase):
        response = apiclient.post(
            reverse("token_obtain_jwt"), login_data, format="json"
        )
        access_token = response.data["access"]
        apiclient.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = apiclient.get(url)
    assert response.status_code == 200
