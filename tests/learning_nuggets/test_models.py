import pytest
from django.urls import reverse
from wagtail.models import Page

from apps.learning_nuggets.models import LearningCategory
from apps.learning_nuggets.models import LearningCenterPage
from apps.learning_nuggets.models import LearningNuggetPage


@pytest.mark.django_db
def test_learning_center_page_is_single_instance():
    main_page = LearningCenterPage.objects.create(path="test", depth=1, title="Test")

    assert LearningCenterPage.objects.first() == main_page
    assert LearningCenterPage.objects.count() == 1


@pytest.mark.django_db
def test_learning_category_slug():
    category = LearningCategory.objects.create(name="Test Category")
    assert category.slug == "test-category", "Slug should be auto-generated from name"


@pytest.mark.django_db
def test_learning_nugget_has_category(client):
    root_page = Page.get_first_root_node()
    category = LearningCategory.objects.create(name="Participants", slug="participants")
    nugget = LearningNuggetPage(
        title="Registration",
        slug="registration",
        category=category,
    )
    root_page.add_child(instance=nugget)
    nugget.save()

    # Ensure the category is assigned correctly
    assert nugget.category is not None
    assert nugget.category.slug == "participants"

    # Ensure URL resolution works
    url = reverse(
        "learning_nuggets:nugget-detail",
        kwargs={"category_slug": "participants", "nugget_slug": "registration"},
    )
    response = client.get(url)
    assert response.status_code == 200
