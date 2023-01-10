import pytest
from dateutil.parser import parse
from django.urls import reverse

from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import freeze_post_phase


@pytest.mark.django_db
def test_app_module_api(user, project_factory, module_factory, apiclient):
    project_1 = project_factory(is_app_accessible=True)
    project_2 = project_factory(is_app_accessible=True)
    project_3 = project_factory(is_app_accessible=True)
    project_4 = project_factory(is_app_accessible=False)
    module_1 = module_factory(project=project_1)
    module_2 = module_factory(project=project_2)
    module_3 = module_factory(project=project_3)
    module_4 = module_factory(project=project_3)
    module_5 = module_factory(project=project_3, is_draft=True)
    module_6 = module_factory(project=project_4)

    url = reverse("app-modules-list")
    response = apiclient.get(url, format="json")
    assert response.status_code == 401

    apiclient.force_authenticate(user=user)
    response = apiclient.get(url, format="json")
    assert response.status_code == 200

    assert any(
        [True for dict in response.data if ("pk" in dict and dict["pk"] == module_1.pk)]
    )
    assert any(
        [True for dict in response.data if ("pk" in dict and dict["pk"] == module_2.pk)]
    )
    assert any(
        [True for dict in response.data if ("pk" in dict and dict["pk"] == module_3.pk)]
    )
    assert any(
        [True for dict in response.data if ("pk" in dict and dict["pk"] == module_4.pk)]
    )
    assert not any(
        [True for dict in response.data if ("pk" in dict and dict["pk"] == module_5.pk)]
    )
    assert not any(
        [True for dict in response.data if ("pk" in dict and dict["pk"] == module_6.pk)]
    )


@pytest.mark.django_db
def test_app_module_api_idea_collection(
    client, apiclient, project_factory, category_factory, label_factory, user
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
    category_1 = category_factory(module=module)
    category_2 = category_factory(module=module)
    label_1 = label_factory(module=module)
    label_2 = label_factory(module=module)

    url = reverse("app-modules-list")
    apiclient.login(username=user.email, password="password")

    response = apiclient.get(url, format="json")
    assert len(project.modules[0].phases) == 2
    assert not response.data[0]["active_phase"]
    assert not response.data[0]["past_phases"]
    assert len(response.data[0]["future_phases"]) == 2

    collect_phase = module.phases.get(type="a4_candy_ideas:collect")
    collect_phase.start_date = parse("2021-07-07 7:10:00 UTC")
    collect_phase.end_date = parse("2021-07-07 12:10:00 UTC")
    collect_phase.save()

    rating_phase = module.phases.get(type="a4_candy_ideas:rating")
    rating_phase.start_date = parse("2021-07-07 12:10:00 UTC")
    rating_phase.end_date = parse("2021-07-07 20:10:00 UTC")
    rating_phase.save()

    response = apiclient.get(url, format="json")
    assert response.status_code == 200
    assert response.data[0]["pk"] == module.pk
    assert {"id": category_1.pk, "name": category_1.name} in response.data[0][
        "categories"
    ]
    assert {"id": category_2.pk, "name": category_2.name} in response.data[0][
        "categories"
    ]
    assert {"id": label_1.pk, "name": label_1.name} in response.data[0]["labels"]
    assert {"id": label_2.pk, "name": label_2.name} in response.data[0]["labels"]
    assert not response.data[0]["active_phase"]
    assert len(response.data[0]["past_phases"]) == 2
    assert not response.data[0]["future_phases"]

    with freeze_phase(collect_phase):
        apiclient.login(username=initiator.email, password="password")
        response = apiclient.get(url, format="json")
        assert response.data[0]["has_idea_adding_permission"] is True
        assert response.data[0]["active_phase"]["name"] == "Collect phase"
        assert response.data[0]["future_phases"][0]["name"] == "Rating phase"

        apiclient.login(username=user.email, password="password")
        response = apiclient.get(url, format="json")
        assert response.data[0]["has_idea_adding_permission"] is True

    with freeze_phase(rating_phase):
        apiclient.login(username=initiator.email, password="password")
        response = apiclient.get(url, format="json")
        assert response.data[0]["has_idea_adding_permission"] is True
        assert response.data[0]["active_phase"]["name"] == "Rating phase"
        assert response.data[0]["past_phases"][0]["name"] == "Collect phase"

        apiclient.login(username=user.email, password="password")
        response = apiclient.get(url, format="json")
        assert response.data[0]["has_idea_adding_permission"] is False

    with freeze_post_phase(rating_phase):
        apiclient.login(username=initiator.email, password="password")
        response = apiclient.get(url, format="json")
        assert response.data[0]["has_idea_adding_permission"] is True
        assert not response.data[0]["active_phase"]
        assert not response.data[0]["future_phases"]
        assert len(response.data[0]["past_phases"]) == 2
        assert response.data[0]["past_phases"][0]["name"] == "Collect phase"
        assert response.data[0]["past_phases"][1]["name"] == "Rating phase"

        apiclient.login(username=user.email, password="password")
        response = apiclient.get(url, format="json")
        assert response.data[0]["has_idea_adding_permission"] is False


@pytest.mark.django_db
def test_app_module_api_poll(client, apiclient, project_factory, user):
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

    url = reverse("app-modules-list")
    apiclient.login(username=user.email, password="password")
    response = apiclient.get(url, format="json")
    assert not response.data[0]["active_phase"]

    assert len(project.modules[0].phases) == 1
    phase = module.phases[0]
    phase.start_date = parse("2021-07-07 7:10:00 UTC")
    phase.end_date = parse("2021-07-07 12:10:00 UTC")
    phase.save()

    response = apiclient.get(url, format="json")
    assert response.status_code == 200
    assert response.data[0]["pk"] == module.pk
    assert response.data[0]["labels"] is False
    assert response.data[0]["categories"] is False
    assert not response.data[0]["active_phase"]
    assert not response.data[0]["future_phases"]
    assert len(response.data[0]["past_phases"]) == 1

    apiclient.logout()

    with freeze_phase(phase):
        response = apiclient.get(url, format="json")
        assert response.status_code == 401
        apiclient.login(username=initiator.email, password="password")
        response = apiclient.get(url, format="json")
        assert response.data[0]["has_idea_adding_permission"] is True
        assert response.data[0]["active_phase"]["name"] == "Voting phase"

        apiclient.login(username=user.email, password="password")
        response = apiclient.get(url, format="json")
        assert response.data[0]["has_idea_adding_permission"] is False

    with freeze_post_phase(phase):
        apiclient.login(username=initiator.email, password="password")
        response = apiclient.get(url, format="json")
        assert response.data[0]["has_idea_adding_permission"] is True
        assert len(response.data[0]["past_phases"]) == 1
        assert response.data[0]["past_phases"][0]["name"] == "Voting phase"

        apiclient.login(username=user.email, password="password")
        response = apiclient.get(url, format="json")
        assert response.data[0]["has_idea_adding_permission"] is False
