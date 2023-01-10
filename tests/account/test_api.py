import tempfile

import pytest
from django.urls import reverse
from PIL import Image
from rest_framework import status


@pytest.mark.django_db
def test_allowed_methods(apiclient, user):
    url = reverse("api-account")
    apiclient.login(username=user.email, password="password")
    data = {"username": "changed name"}

    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK

    response = apiclient.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK

    response = apiclient.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = apiclient.patch(url, data=data, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = apiclient.delete(url, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_permissions(apiclient, admin, user):
    url = reverse("api-account")

    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    apiclient.login(username=admin.email, password="password")
    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK

    apiclient.login(username=user.email, password="password")
    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_returns_logged_in_user(apiclient, admin, user):
    url = reverse("api-account")

    apiclient.login(username=admin.email, password="password")
    response = apiclient.get(url, format="json")
    assert "username" in response.data
    assert response.data["username"] == admin.username

    apiclient.login(username=user.email, password="password")
    response = apiclient.get(url, format="json")
    assert "username" in response.data
    assert response.data["username"] == user.username


@pytest.mark.django_db
def test_user_can_change_account_settings(apiclient, user):
    url = reverse("api-account")
    apiclient.login(username=user.email, password="password")

    image = Image.new("RGBA", size=(600, 600), color=(155, 0, 0))
    file = tempfile.NamedTemporaryFile(suffix=".png")
    image.save(file)

    with open(file.name, "rb") as image_data:
        data = {"username": "changed name", "user_image": image_data}
        response = apiclient.put(url, data, format="multipart")
        assert response.status_code == 200
        img_name = file.name.split("/")[-1]
        assert "user_image" in response.data
        assert response.data["user_image"].endswith(img_name)
        user.refresh_from_db()
        assert user._avatar
        assert user._avatar.name.endswith(img_name)
        assert user.username == "changed name"
