import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_fallback_images(
    apiclient, comment_factory, idea_factory, module_factory, project_factory
):
    project = project_factory()
    project_app = project_factory(is_app_accessible=True)
    module = module_factory(project=project)
    module_app = module_factory(project=project_app)
    idea = idea_factory(module=module)
    idea_app = idea_factory(module=module_app)
    comment = comment_factory(content_object=idea)
    comment_app = comment_factory(content_object=idea_app)

    url = reverse(
        "comments-detail",
        kwargs={
            "pk": comment.pk,
            "content_type": comment.content_type.pk,
            "object_pk": comment.object_pk,
        },
    )
    response = apiclient.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert not response.data["user_image"]
    assert response.data["user_image_fallback"].endswith("svg")

    url = reverse(
        "comments-detail",
        kwargs={
            "pk": comment_app.pk,
            "content_type": comment_app.content_type.pk,
            "object_pk": comment_app.object_pk,
        },
    )
    response = apiclient.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert not response.data["user_image"]
    assert response.data["user_image_fallback"].endswith("png")

    comment_app.is_blocked = True
    comment_app.save()
    response = apiclient.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert not response.data["user_image"]
    assert not response.data["user_image_fallback"]
