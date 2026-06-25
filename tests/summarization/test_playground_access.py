import pytest
from django.urls import reverse

from tests.factories import AdminFactory
from tests.factories import UserFactory


@pytest.mark.django_db
def test_summarization_playground_requires_login(client):
    url = reverse("summarization:test")
    response = client.get(url)
    assert response.status_code == 302
    assert "/login" in response.url


@pytest.mark.django_db
def test_summarization_playground_denies_non_staff_user(client):
    user = UserFactory()
    client.force_login(user)

    response = client.get(reverse("summarization:test"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_summarization_playground_allows_staff_user(client):
    admin = AdminFactory()
    client.force_login(admin)

    response = client.get(reverse("summarization:test"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_summarization_documents_playground_denies_non_staff_user(client):
    user = UserFactory()
    client.force_login(user)

    response = client.get(reverse("summarization:test-documents"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_summarization_export_denies_non_staff_user(client, project_factory):
    user = UserFactory()
    client.force_login(user)
    project = project_factory()

    url = reverse("summarization:test-export", kwargs={"project_id": project.pk})
    response = client.get(url)
    assert response.status_code == 403
