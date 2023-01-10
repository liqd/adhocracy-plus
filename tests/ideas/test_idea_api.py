import tempfile

import pytest
from django.urls import reverse
from PIL import Image
from rest_framework import status

from adhocracy4.test.helpers import freeze_phase
from adhocracy4.test.helpers import freeze_post_phase
from adhocracy4.test.helpers import setup_phase
from apps.ideas import phases
from apps.ideas.models import Idea


@pytest.mark.django_db
def test_idea_list_api(idea_factory, apiclient):
    idea_1 = idea_factory()
    module = idea_1.module
    idea_2 = idea_factory(module=module)
    idea_3 = idea_factory(module=module)
    idea_other_module = idea_factory()

    assert module != idea_other_module.module

    url = reverse("ideas-list", kwargs={"module_pk": module.pk})
    response = apiclient.get(url, format="json")

    assert response.status_code == 200
    assert any(
        [True for dict in response.data if ("pk" in dict and dict["pk"] == idea_1.pk)]
    )
    assert any(
        [True for dict in response.data if ("pk" in dict and dict["pk"] == idea_2.pk)]
    )
    assert any(
        [True for dict in response.data if ("pk" in dict and dict["pk"] == idea_3.pk)]
    )
    assert not any(
        [
            True
            for dict in response.data
            if ("pk" in dict and dict["pk"] == idea_other_module.pk)
        ]
    )


@pytest.mark.django_db
def test_idea_serializer(idea_factory, comment_factory, apiclient, label_factory):
    idea = idea_factory(
        description="<p>description with a <strong>bold</strong> bit</p>"
    )
    comment = comment_factory(content_object=idea)
    comment_factory(content_object=idea)
    comment_factory(content_object=idea)
    comment_factory(content_object=idea)
    comment_factory(content_object=comment)
    label1 = label_factory(module=idea.module)
    label2 = label_factory(module=idea.module)
    idea.labels.add(label1, label2)

    url = reverse("ideas-list", kwargs={"module_pk": idea.module.pk})
    response = apiclient.get(url, format="json")

    assert response.status_code == 200
    assert response.data[0]["description"] == "description with a bold bit"
    assert response.data[0]["comment_count"] == 4
    assert response.data[0]["labels"] == [
        {"id": label1.pk, "name": label1.name},
        {"id": label2.pk, "name": label2.name},
    ]
    assert not response.data[0]["category"]
    assert response.data[0]["has_rating_permission"] is False
    assert response.data[0]["has_commenting_permission"] is False
    assert response.data[0]["has_changing_permission"] is False
    assert response.data[0]["has_deleting_permission"] is False


@pytest.mark.django_db
def test_anonymous_cannot_add_idea(apiclient, idea):
    url = reverse("ideas-list", kwargs={"module_pk": idea.module.pk})

    response = apiclient.get(url, format="json")
    assert response.data[0]["has_rating_permission"] is False
    assert response.data[0]["has_commenting_permission"] is False
    assert response.data[0]["has_changing_permission"] is False
    assert response.data[0]["has_deleting_permission"] is False

    data = {}
    response = apiclient.post(url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_initiator_can_add_idea(
    apiclient, admin, phase_factory, idea_factory, category_factory, label_factory
):
    phase, module, project, _ = setup_phase(
        phase_factory, idea_factory, phases.CollectPhase
    )
    url = reverse("ideas-list", kwargs={"module_pk": module.pk})
    category = category_factory(module=module)
    label = label_factory(module=module)
    data = {
        "name": "an idea",
        "description": "this is the description",
        "category": category.pk,
        "labels": [label.pk],
    }
    user = project.organisation.initiators.first()
    apiclient.force_authenticate(user=user)

    response = apiclient.get(url, format="json")
    assert response.data[0]["has_rating_permission"] is True
    assert response.data[0]["has_commenting_permission"] is True
    assert response.data[0]["has_changing_permission"] is True
    assert response.data[0]["has_deleting_permission"] is True

    response = apiclient.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Idea.objects.get(name=data["name"]).description == data["description"]


@pytest.mark.django_db
def test_user_can_add_idea_during_phase(
    apiclient, user, phase_factory, idea_factory, category_factory, label_factory
):
    phase, module, project, _ = setup_phase(
        phase_factory, idea_factory, phases.CollectPhase
    )
    url = reverse("ideas-list", kwargs={"module_pk": module.pk})
    category = category_factory(module=module)
    label = label_factory(module=module)
    data = {
        "name": "an idea",
        "description": "this is the description",
        "category": category.pk,
        "labels": [label.pk],
    }
    apiclient.force_authenticate(user=user)
    with freeze_phase(phase):
        response = apiclient.get(url, format="json")
        assert response.data[0]["has_rating_permission"] is False
        assert response.data[0]["has_commenting_permission"] is True
        assert response.data[0]["has_changing_permission"] is False
        assert response.data[0]["has_deleting_permission"] is False

        response = apiclient.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Idea.objects.get(name=data["name"]).description == data["description"]


@pytest.mark.django_db
def test_user_cannot_add_idea_after_phase(
    apiclient, user, phase_factory, idea_factory, category_factory, label_factory
):
    phase, module, project, _ = setup_phase(
        phase_factory, idea_factory, phases.CollectPhase
    )
    url = reverse("ideas-list", kwargs={"module_pk": module.pk})
    category = category_factory(module=module)
    label = label_factory(module=module)
    data = {
        "name": "an idea",
        "description": "this is the description",
        "category": category.pk,
        "labels": [label.pk],
    }
    apiclient.force_authenticate(user=user)
    with freeze_post_phase(phase):
        response = apiclient.get(url, format="json")
        assert response.data[0]["has_rating_permission"] is False
        assert response.data[0]["has_commenting_permission"] is False
        assert response.data[0]["has_changing_permission"] is False
        assert response.data[0]["has_deleting_permission"] is False

        response = apiclient.post(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_initiator_can_update_idea(apiclient, idea):
    url = reverse("ideas-detail", kwargs={"module_pk": idea.module.pk, "pk": idea.pk})
    data = {
        "name": "a changed idea",
        "description": "this is the changed description",
    }
    user = idea.module.project.organisation.initiators.first()
    apiclient.force_authenticate(user=user)

    response = apiclient.get(url, format="json")
    assert response.data["has_rating_permission"] is True
    assert response.data["has_commenting_permission"] is True
    assert response.data["has_changing_permission"] is True
    assert response.data["has_deleting_permission"] is True

    response = apiclient.patch(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    idea = Idea.objects.first()
    assert idea.name == data["name"]
    assert idea.description == data["description"]


@pytest.mark.django_db
def test_user_can_update_idea_during_phase(apiclient, phase_factory, idea_factory):
    phase, _, project, item = setup_phase(
        phase_factory, idea_factory, phases.CollectPhase
    )
    url = reverse("ideas-detail", kwargs={"module_pk": item.module.pk, "pk": item.pk})
    data = {
        "name": "a changed idea",
        "description": "this is the changed description",
    }
    user = item.creator
    apiclient.force_authenticate(user=user)
    with freeze_phase(phase):
        response = apiclient.get(url, format="json")
        assert response.data["has_rating_permission"] is False
        assert response.data["has_commenting_permission"] is True
        assert response.data["has_changing_permission"] is True
        assert response.data["has_deleting_permission"] is True

        response = apiclient.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        idea = Idea.objects.first()
        assert idea.name == data["name"]
        assert idea.description == data["description"]


@pytest.mark.django_db
def test_user_cannot_update_idea_after_phase(apiclient, phase_factory, idea_factory):
    phase, _, project, item = setup_phase(
        phase_factory, idea_factory, phases.CollectPhase
    )
    url = reverse("ideas-detail", kwargs={"module_pk": item.module.pk, "pk": item.pk})
    data = {
        "name": "a changed idea",
        "description": "this is the changed description",
    }
    user = item.creator
    apiclient.force_authenticate(user=user)
    with freeze_post_phase(phase):
        response = apiclient.get(url, format="json")
        assert response.data["has_rating_permission"] is False
        assert response.data["has_commenting_permission"] is False
        assert response.data["has_changing_permission"] is False
        assert response.data["has_deleting_permission"] is False

        response = apiclient.patch(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_can_add_and_delete_idea_image_during_phase(
    apiclient, bigImage, phase_factory, idea_factory
):
    phase, _, project, idea = setup_phase(
        phase_factory, idea_factory, phases.CollectPhase
    )
    url = reverse("ideas-detail", kwargs={"module_pk": idea.module.pk, "pk": idea.pk})
    user = idea.creator
    apiclient.force_authenticate(user=user)
    with freeze_phase(phase):
        response = apiclient.get(url, format="json")
        assert response.status_code == 200

        # add image
        image = Image.new("RGBA", size=(600, 600), color=(155, 0, 0))
        file = tempfile.NamedTemporaryFile(suffix=".png")
        image.save(file)
        with open(file.name, "rb") as image_data:
            data = {"image": image_data}
            response = apiclient.patch(url, data, format="multipart")
            assert response.status_code == 200
            img_name = file.name.split("/")[-1]
            assert response.data["image"].endswith(img_name)
            idea.refresh_from_db()
            assert idea.image
            assert idea.image.name.endswith(img_name)

        # delete image
        data = {"image_deleted": True}
        response = apiclient.patch(url, data, format="json")
        assert response.status_code == 200
        idea.refresh_from_db()
        assert not idea.image
