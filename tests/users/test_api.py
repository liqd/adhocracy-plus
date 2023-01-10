import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_allowed_methods(apiclient, user):
    url = reverse("users-detail", kwargs={"pk": user.pk})
    apiclient.login(username=user.email, password="password")
    data = {"username": "changed name"}

    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK

    response = apiclient.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = apiclient.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = apiclient.patch(url, data=data, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = apiclient.delete(url, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_permissions(apiclient, admin, user):
    url = reverse("users-detail", kwargs={"pk": user.pk})

    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    apiclient.login(username=admin.email, password="password")
    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK

    apiclient.login(username=user.email, password="password")
    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK

    url = reverse("users-detail", kwargs={"pk": admin.pk})

    apiclient.login(username=admin.email, password="password")
    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK

    apiclient.login(username=user.email, password="password")
    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_is_self(apiclient, admin, user):
    url = reverse("users-detail", kwargs={"pk": user.pk})

    apiclient.login(username=admin.email, password="password")
    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "is_self" in response.data
    assert not response.data["is_self"]

    apiclient.login(username=user.email, password="password")
    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "is_self" in response.data
    assert response.data["is_self"]
